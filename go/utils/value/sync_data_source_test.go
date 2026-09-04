// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"context"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"maps"
	"slices"
	"sync"
	"testing"
	"time"

	"golang.org/x/sync/errgroup"
	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"

	"go.chromium.org/turboci/proto/go/utils/internal/test/assert"
)

func TestDataSource(t *testing.T) {
	t.Parallel()

	mkBin := func() *orchestratorpb.ValueData {
		ret := &orchestratorpb.ValueData{}
		ret.SetBinary(&anypb.Any{TypeUrl: "binary", Value: []byte("binary")})
		return ret
	}
	mkJson := func() *orchestratorpb.ValueData {
		ret := &orchestratorpb.ValueData{}
		ret.SetJson(orchestratorpb.ValueData_JsonAny_builder{
			TypeUrl: proto.String("json"),
			Value:   proto.String("json"),
		}.Build())
		return ret
	}

	dat := map[string]*orchestratorpb.ValueData{
		"1": mkBin(),
		"2": mkBin(),
		"3": mkBin(),
		"4": mkJson(),
		"5": mkBin(),
	}

	ds := SyncDataSourceFromMap(dat)

	assert.True(t, ds.Retrieve("1").HasBinary())

	assert.True(t, ds.Retrieve("4").HasJson())

	assert.Nil(t, ds.Retrieve("NX"))

	ds.Intern("2", mkJson())
	ds.Intern("4", mkBin())
	ds.Intern("6", mkJson())

	// At this point, 1, 3, 5 are binary and 2, 4, 6 are JSON.

	assert.True(t, ds.Retrieve("2").HasJson())

	assert.True(t, ds.Retrieve("4").HasJson())

	assert.Nil(t, ds.Retrieve("NX"))
	assert.Equal(t, int64(6+proto.Size(mkBin())*3+proto.Size(mkJson())*3), ds.DataSize())
}

type mockDatum struct {
	digest Digest
	dat    *orchestratorpb.ValueData
}

func genMockData(numChunks, dataPerChunk, digestTrunc int) [][]mockDatum {
	chunks := make([][]mockDatum, numChunks)
	for c := range chunks {
		data := make([]mockDatum, dataPerChunk)
		for i := range dataPerChunk {
			binary := &anypb.Any{
				TypeUrl: "bogus",
				Value:   fmt.Appendf(nil, "chunk-%d-dgst-%d", c, i),
			}
			sum := sha256.Sum224(binary.Value)
			data[i].digest = Digest(base64.RawURLEncoding.EncodeToString(sum[:digestTrunc]))
			if i%2 == 0 {
				data[i].dat = orchestratorpb.ValueData_builder{
					Binary: binary,
				}.Build()
			} else {
				data[i].dat = orchestratorpb.ValueData_builder{
					Json: orchestratorpb.ValueData_JsonAny_builder{
						TypeUrl: &binary.TypeUrl,
						Value:   proto.String(string(binary.Value)),
					}.Build(),
				}.Build()
			}
		}
		chunks[c] = data
	}
	return chunks
}

func TestDataSourceStress(t *testing.T) {
	// This is intended to get the race detector to squawk if we did something
	// wrong.

	const writerChunk = 3000
	const digestBytes = 3
	const numReaders = 1
	const numWriters = 5

	chunks := genMockData(numWriters, writerChunk, digestBytes)

	ds := &SyncDataSource{}

	ctx, cancel := context.WithCancel(t.Context())
	defer cancel()

	for range numReaders {
		go func() {
			for {
				select {
				case <-ctx.Done():
					return
				default:
					time.Sleep(time.Millisecond)
					ds.ToMap()
				}
			}
		}()
	}

	eg := errgroup.Group{}

	for w := range numWriters {
		eg.Go(func() error {
			for _, datum := range chunks[w] {
				ds.Intern(datum.digest, datum.dat)
			}
			return nil
		})
	}

	eg.Wait()
	cancel()
}

func BenchmarkSyncDataSource(b *testing.B) {
	const writerData = 30000
	const writeSize = 100
	const digestBytes = 3
	const numReaders = 1
	const numWriters = 1

	ds := &SyncDataSource{}
	maps := make([][]map[string]*orchestratorpb.ValueData, numWriters)
	for i, dataForWriter := range genMockData(numWriters, writerData, digestBytes) {
		w := make([]map[string]*orchestratorpb.ValueData, 0, writerData/writeSize)
		for chunk := range slices.Chunk(dataForWriter, writeSize) {
			m := make(map[string]*orchestratorpb.ValueData, writeSize)
			for _, dat := range chunk {
				m[string(dat.digest)] = dat.dat
			}
			w = append(w, m)
		}
		maps[i] = w
	}

	b.ReportAllocs()
	for b.Loop() {
		ctx, cancel := context.WithCancel(b.Context())
		defer cancel()

		for range numReaders {
			go func() {
				for {
					select {
					case <-ctx.Done():
						return
					default:
						time.Sleep(time.Millisecond)
						ds.ToMap()
					}
				}
			}()
		}

		eg := errgroup.Group{}
		for w := range numWriters {
			eg.Go(func() error {
				for _, write := range maps[w] {
					ds.UpdateFrom(write)
				}
				return nil
			})
		}

		eg.Wait()
		cancel()
	}
}

type mutexMap struct {
	mu   sync.RWMutex
	data map[string]*orchestratorpb.ValueData
}

// Note: a previous version of DataSource made Intern accept an entire map,
// just to allow this type of simplistic implementation.
//
// It turns out that most uses (except for merging in another map) really
// want a singular Intern method.
//
// We keep this mutexMap just for benchmarking/historical/comparison purposes
// though.
//
// var _ DataSource = (*mutexMap)(nil)

func (m *mutexMap) Retrieve(digest string) *orchestratorpb.ValueData {
	m.mu.RLock()
	defer m.mu.RUnlock()

	return m.data[digest]
}

func (m *mutexMap) Intern(data map[string]*orchestratorpb.ValueData) {
	m.mu.Lock()
	defer m.mu.Unlock()

	for digest, dat := range data {
		m.data[digest] = PickData(m.data[digest], dat)
	}
}

func (m *mutexMap) ToMap() map[string]*orchestratorpb.ValueData {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return maps.Clone(m.data)
}

func BenchmarkMutexMap(b *testing.B) {
	const writerData = 30000
	const writeSize = 100
	const digestBytes = 3
	const numReaders = 1
	const numWriters = 1

	ds := &mutexMap{data: map[string]*orchestratorpb.ValueData{}}
	maps := make([][]map[string]*orchestratorpb.ValueData, numWriters)
	for i, dataForWriter := range genMockData(numWriters, writerData, digestBytes) {
		w := make([]map[string]*orchestratorpb.ValueData, 0, writerData/writeSize)
		for chunk := range slices.Chunk(dataForWriter, writeSize) {
			m := make(map[string]*orchestratorpb.ValueData, writeSize)
			for _, dat := range chunk {
				m[string(dat.digest)] = dat.dat
			}
			w = append(w, m)
		}
		maps[i] = w
	}

	b.ReportAllocs()
	for b.Loop() {
		ctx, cancel := context.WithCancel(b.Context())
		defer cancel()

		for range numReaders {
			go func() {
				for {
					select {
					case <-ctx.Done():
						return
					default:
						time.Sleep(time.Millisecond)
						ds.ToMap()
					}
				}
			}()
		}

		eg := errgroup.Group{}
		for w := range numWriters {
			eg.Go(func() error {
				for _, write := range maps[w] {
					ds.Intern(write)
				}
				return nil
			})
		}

		eg.Wait()
		cancel()
	}
}
