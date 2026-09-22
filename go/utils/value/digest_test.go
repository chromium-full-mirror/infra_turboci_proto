// Copyright 2026 The Chromium Authors
// Use of this source code is governed by a BSD-style license that can be
// found in the LICENSE file.

package value

import (
	"bytes"
	"crypto/sha256"
	"encoding/base64"
	"strings"
	"testing"

	"google.golang.org/protobuf/proto"
	"google.golang.org/protobuf/types/known/anypb"
	"google.golang.org/protobuf/types/known/emptypb"
	"google.golang.org/protobuf/types/known/structpb"

	orchestratorpb "go.chromium.org/turboci/proto/go/graph/orchestrator/v1"
)

func TestComputeDigest(t *testing.T) {
	t.Parallel()

	cases := []struct {
		name string
		msg  proto.Message
		want Digest
	}{
		{
			"empty",
			&emptypb.Empty{},
			"zC1HiB0gq_T1muuCh5VIAoC4FjWvxp00E9waqU1YMhkrAQ",
		},
		{
			"float_val",
			structpb.NewNumberValue(123.456),
			"aexUjcBYp_UhSBsbm6TwadrRm0ZAYUrR5mRAKiJ2XtQ2AQ",
		},
		{
			"long_string",
			structpb.NewStringValue(strings.Repeat("this is a very long string", 40000)),
			"tvpg39g5kBqzdMKxPOWxvE82_CR13ZmPUmuaq186WyCzvT8B",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			t.Parallel()

			apb, err := anypb.New(tc.msg)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			dgst := ComputeDigest(apb)
			if dgst != tc.want {
				t.Errorf("got %q, want %q", dgst, tc.want)
			}

			dgstPb, err := dgst.ToProto()
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			wantSize := proto.Size(apb)
			enc, err := proto.Marshal(apb)
			if err != nil {
				t.Fatalf("unexpected error: %v", err)
			}
			if len(enc) != wantSize {
				t.Errorf("got len(enc) = %d, want %d", len(enc), wantSize)
			}

			detEnc := DeterministicallySerializeAny(apb)
			if len(detEnc) != wantSize {
				t.Errorf("got len(detEnc) = %d, want %d", len(detEnc), wantSize)
			}

			dec := &anypb.Any{}
			if err := proto.Unmarshal(detEnc, dec); err != nil {
				t.Fatalf("unexpected error: %v", err)
			}

			if !proto.Equal(dec, apb) {
				t.Errorf("expected proto.Equal(dec, apb) to be true")
			}

			sha := sha256.Sum256(detEnc)
			if !bytes.Equal(sha[:], dgstPb.GetHash()) {
				t.Errorf("hash mismatch: got %x, want %x", dgstPb.GetHash(), sha[:])
			}

			if got, want := dgstPb.GetSizeBytes(), uint64(wantSize); got != want {
				t.Errorf("got SizeBytes = %d, want %d", got, want)
			}
		})
	}
}

func TestDigestToProtoErrors(t *testing.T) {
	t.Parallel()

	b64 := func(hsh, size, algo []byte) Digest {
		toEnc := make([]byte, 0, len(hsh)+len(size)+len(algo))
		toEnc = append(toEnc, hsh...)
		toEnc = append(toEnc, size...)
		toEnc = append(toEnc, algo...)
		return Digest(base64.RawURLEncoding.EncodeToString(toEnc))
	}

	cases := []struct {
		name    string
		digest  Digest
		wantErr string
	}{
		{
			name:    "bad_base64",
			digest:  "heloworld",
			wantErr: "illegal base64",
		},
		{
			name:    "missing_algo",
			digest:  "",
			wantErr: "missing algorithm",
		},
		{
			name:    "bad_algo",
			digest:  b64(make([]byte, 32), []byte{1}, []byte{32}),
			wantErr: "bad algorithm",
		},
		{
			name:    "small_hash",
			digest:  b64(make([]byte, 20), []byte{1}, []byte{byte(orchestratorpb.ValueHashAlgo_VALUE_HASH_ALGO_SHA256)}),
			wantErr: "insufficient bytes for hash",
		},
		{
			name:    "extra_size",
			digest:  b64(make([]byte, 32), []byte{1, 1, 1}, []byte{byte(orchestratorpb.ValueHashAlgo_VALUE_HASH_ALGO_SHA256)}),
			wantErr: "extra bytes while decoding size",
		},
	}

	for _, tc := range cases {
		t.Run(tc.name, func(t *testing.T) {
			_, err := tc.digest.ToProto()
			if err == nil || !strings.Contains(err.Error(), tc.wantErr) {
				t.Fatalf("expected error containing %q, got %v", tc.wantErr, err)
			}
		})
	}
}
