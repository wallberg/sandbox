package taocp

import (
	"fmt"
	"reflect"
	"testing"
)

func TestParsePlacementPairs(t *testing.T) {

	cases := []struct {
		s     string // string to parse
		pairs []int  // sorted pairs
		err   bool   // true if error is expected
	}{
		{
			"[14-7]2 5[0-3]",
			[]int{65538, 262146, 327680, 327681, 327682, 327683, 393218,
				458754},
			false,
		},
		{
			"[0-2][a-c]",
			[]int{10, 11, 12,
				65546, 65547, 65548,
				131082, 131083, 131084,
			},
			false,
		},
		{
			"",
			nil,
			true,
		},
		{
			"x",
			nil,
			true,
		},
	}

	for _, c := range cases {
		pairs, err := ParsePlacementPairs(c.s)

		if (err != nil) != c.err {
			t.Errorf("(err != nil) = %v; want %v", err != nil, c.err)
		}

		if !reflect.DeepEqual(c.pairs, pairs) {
			t.Errorf("pairs = %v; want %v", pairs, c.pairs)
		}
	}
}

func TestBasePlacements(t *testing.T) {

	cases := []struct {
		first      []int
		placements [][]int
		transform  bool
	}{
		{
			[]int{65536},
			[][]int{{0}},
			true,
		},
		{
			[]int{1, 2, 3},
			[][]int{
				{0, 1, 2},
				{0, 65536, 131072},
			},
			true,
		},
		{
			[]int{1, 2, 3},
			[][]int{
				{0, 1, 2},
			},
			false,
		},
		{
			[]int{0, 1, 2, 65536},
			[][]int{
				{0, 1, 2, 65536},
				{0, 1, 2, 65538},
				{0, 1, 65536, 131072},
				{0, 1, 65537, 131073},
				{0, 65536, 65537, 65538},
				{0, 65536, 131072, 131073},
				{1, 65537, 131072, 131073},
				{2, 65536, 65537, 65538},
			},
			true,
		},
	}

	for _, c := range cases {
		placements := BasePlacements(c.first, c.transform)

		if !reflect.DeepEqual(placements, c.placements) {
			fmt.Println(placements)
			fmt.Println(c.placements)
			t.Errorf("placements = %v; want %v", placements, c.placements)
		}
	}
}

func TestLoadPolyominoes(t *testing.T) {

	sets := LoadPolyominoes()

	cases := []struct {
		name  string // name of the set
		count int    // number of shapes in the set
	}{
		{"1", 1},
		{"2", 1},
		{"3", 2},
		{"4", 5},
		{"5", 12},
	}

	for _, c := range cases {
		if set, ok := sets[c.name]; !ok {
			t.Errorf("Did not find set name='%s'", c.name)
		} else {
			if len(set.Shapes) != c.count {
				t.Errorf("Set '%s' has %d shapes; want %d",
					set.Name, len(set.Shapes), c.count)
			}
		}
	}
}

func TestPolyominoes(t *testing.T) {
	cases := []struct {
		shapes []string // names of the piece shapes
		board  string   // name of the board shape
		count  int      // number of expected results
	}{
		{[]string{"5"}, "3x20", 8},
		{[]string{"1"}, "1x1", 1},
		{[]string{"2"}, "1x1", 0},
		{[]string{"1", "2"}, "2x2", 0},
		{[]string{"1", "2"}, "2x2-1", 2},
		{[]string{"2", "3"}, "2x3", 0},
		{[]string{"1", "2", "3"}, "3x3", 48},
		{[]string{"2", "3"}, "3x3-1", 4},
		{[]string{"1", "2", "3", "4"}, "5x6-1", 100593}, // tautology
		// {[]string{"4", "5"}, "8x8", 0},                   // too slow
		// {[]string{"1", "2", "3", "4", "5"}, "5x18-1", 0}, // too slow
	}

	for _, c := range cases {
		items, options, sitems := Polyominoes(c.shapes, c.board)

		if c.board == "8x8" {
			fmt.Println(items)
			for _, option := range options {
				fmt.Println(option)
			}
		}

		// Generate solutions
		count := 0
		if len(options) > 0 {
			stats := &Stats{Debug: false, Progress: true, Delta: 10000000}
			ExactCover(items, options, sitems, stats,
				func(solution [][]string) bool {
					count++
					return true
				})
		}

		if count != c.count {
			t.Errorf("Found %d solutions for shape sets=%v, board=%s; want %d", count, c.shapes, c.board, c.count)
		}
	}
}