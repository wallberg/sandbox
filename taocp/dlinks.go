package taocp

import (
	"fmt"
)

// Explore Dancing Links from The Art of Computer Programming, Volume 4,
// Fascicle 5, Mathematical Preliminaries Redux; Introduction to Backtracking;
// Dancing Links, 2020
//
// §7.2.2.1 Dancing Links

// Stats is a struct for tracking ExactCover statistics and reporting
// runtime progress
type Stats struct {
	Progress  bool  // Display runtime progress
	MaxLevel  int   // Maximum level reached
	Delta     int   // Display progress every Delta number of Nodes
	Theta     int   // Display progress at next Theta number of Nodes
	Levels    []int // Count of times each level is intered
	Nodes     int   // Count of nodes processed
	Solutions int   // Count of solutions returned
	Debug     bool  // Enable debug logging
}

// ExactCover implements Algorithm X, exact cover via dancing links.
//
// Arguments:
// items     -- sorted list of primary items
// options   -- list of list of options; every option must contain at least one
// 			 primary item
// secondary -- sorted list of secondary items
// stats     -- dictionary to accumulate runtime statistics
// progress  -- display progress report, every 'progress' number of level
// 			 entries
//
func ExactCover(items []string, options [][]string, secondary []string,
	stats *Stats, visit func(solution [][]string)) {

	var (
		n1    int      // number of primary items
		n2    int      // number of secondary items
		n     int      // total number of items
		name  []string // name of the item
		llink []int    // right link of the item
		rlink []int    // left link of the item
		top   []int
		llen  []int
		ulink []int
		dlink []int
		level int
		state []int // search state
		debug bool  // is debug enabled?
	)

	dump := func() {
		i := 0
		for rlink[i] != 0 {
			i = rlink[i]
			fmt.Print("  ", name[i])
			x := i
			for dlink[x] != i {
				x = dlink[x]
				fmt.Print(" ", name[top[x]])
			}
			fmt.Println()
		}
		fmt.Println("---")
	}

	initialize := func() {
		n1 = len(items)
		n2 = len(secondary)
		n = n1 + n2

		if stats != nil {
			stats.Theta = stats.Delta
			stats.MaxLevel = -1
			stats.Levels = make([]int, n)
			stats.Nodes = 0
			stats.Solutions = 0
			debug = stats.Debug
		}

		// Fill out the item tables
		name = make([]string, n+2)
		llink = make([]int, n+2)
		rlink = make([]int, n+2)

		for j, item := range append(items, secondary...) {
			i := j + 1
			name[i] = item
			llink[i] = i - 1
			rlink[i-1] = i
		}

		// two doubly linked lists, primary and secondary
		// head of the primary list is at i=0
		// head of the secondary list is at i=n+1
		llink[n+1] = n
		rlink[n] = n + 1
		llink[n1+1] = n + 1
		rlink[n+1] = n1 + 1
		llink[0] = n1
		rlink[n1] = 0

		if debug {
			fmt.Println("name", name)
			fmt.Println("llink", llink)
			fmt.Println("rlink", rlink)
		}

		// Fill out the option tables
		nOptions := len(options)
		nOptionItems := 0
		for _, option := range options {
			nOptionItems += len(option)
		}
		size := n + 1 + nOptions + 1 + nOptionItems

		top = make([]int, size)
		llen = top[0 : n+1] // first n+1 elements of top
		ulink = make([]int, size)
		dlink = make([]int, size)

		// Set empty list for each item
		for i := 1; i <= n; i++ {
			llen[i] = 0
			ulink[i] = i
			dlink[i] = i
		}

		// Insert each of the options and their items
		x := n + 1
		spacer := 0
		top[x] = spacer
		spacerX := x

		// Iterate over each option
		for _, option := range options {
			// Iterate over each item in this option
			for _, item := range option {
				x++
				i := 0
				for _, value := range name {
					if value == item {
						break
					}
					i++
				}
				top[x] = i

				// Insert into the option list for this item
				llen[i]++ // increase the size by one
				head := i
				tail := i
				for dlink[tail] != head {
					tail = dlink[tail]
				}

				dlink[tail] = x
				ulink[x] = tail

				ulink[head] = x
				dlink[x] = head
			}

			// Insert spacer at end of each option
			dlink[spacerX] = x
			x++
			ulink[x] = spacerX + 1

			spacer--
			top[x] = spacer
			spacerX = x
		}

		if debug {
			fmt.Println("top", top)
			fmt.Println("llen", llen)
			fmt.Println("ulink", ulink)
			fmt.Println("dlink", dlink)
		}

		level = 0
		state = make([]int, nOptions)

		if debug {
			dump()
		}
	}

	showProgress := func() {

		est := 0.0 // estimate of percentage done
		tcum := 1

		fmt.Printf("Current level %d of max %d\n", level, stats.MaxLevel)

		// Iterate over the options
		for _, p := range state[0:level] {
			// Cyclically gather the items in the option, beginning at p
			fmt.Print("  ")
			q := p
			for {
				fmt.Print(name[top[q]] + " ")
				q++
				if top[q] <= 0 {
					q = ulink[q]
				}
				if q == p {
					break
				}
			}

			// Get position stats for this option
			i := top[p]
			q = dlink[i]
			k := 1
			for q != p && q != i {
				q = dlink[q]
				k++
			}

			if q != i {
				fmt.Printf(" %d of %d\n", k, llen[i])
				tcum *= llen[i]
				est += float64(k-1) / float64(tcum)
			} else {
				fmt.Println(" not in this list")
			}
		}

		est += 1.0 / float64(2*tcum)

		fmt.Printf("  solutions=%d, nodes=%d, est=%4.4f\n",
			stats.Solutions, stats.Nodes, est)
		fmt.Println("---")
	}

	lvisit := func() {
		// Iterate over the options
		options := make([][]string, 0)
		for i, p := range state[0:level] {
			options = append(options, make([]string, 0))
			// Move back to first element in the option
			for top[p-1] > 0 {
				p--
			}
			// Iterate over elements in the option
			q := p
			for top[q] > 0 {
				options[i] = append(options[i], name[top[q]])
				q++
			}
		}

		visit(options)
	}

	// mrv selects the next item to try using the Minimum Remaining
	// Values heuristic.
	mrv := func() int {

		i := 0
		theta := -1
		p := rlink[0]
		for p != 0 {
			lambda := llen[p]
			if lambda < theta || theta == -1 {
				theta = lambda
				i = p
				if theta == 0 {
					return i
				}
			}
			p = rlink[p]
		}

		return i
	}

	hide := func(p int) {
		q := p + 1
		for q != p {
			x := top[q]
			u, d := ulink[q], dlink[q]
			if x <= 0 {
				q = u // q was a spacer
			} else {
				dlink[u], ulink[d] = d, u
				llen[x]--
				q++
			}
		}
	}

	cover := func(i int) {
		p := dlink[i]
		for p != i {
			hide(p)
			p = dlink[p]
		}
		l, r := llink[i], rlink[i]
		rlink[l], llink[r] = r, l
	}

	unhide := func(p int) {
		q := p - 1
		for q != p {
			x := top[q]
			u, d := ulink[q], dlink[q]
			if x <= 0 {
				q = d // q was a spacer
			} else {
				dlink[u], ulink[d] = q, q
				llen[x]++
				q--
			}
		}
	}

	uncover := func(i int) {
		l, r := llink[i], rlink[i]
		rlink[l], llink[r] = i, i
		p := ulink[i]
		for p != i {
			unhide(p)
			p = ulink[p]
		}
	}

	// X1 [Initialize.]
	initialize()

	var (
		i int
		j int
		p int
	)

X2:
	// X2. [Enter level l.]
	if debug {
		fmt.Printf("X2. level=%d, x=%v\n", level, state[0:level])
	}

	if stats != nil {
		stats.Levels[level]++
		stats.Nodes++

		if stats.Progress {
			if level > stats.MaxLevel {
				stats.MaxLevel = level
			}
			if stats.Nodes >= stats.Theta {
				showProgress()
				stats.Theta += stats.Delta
			}
		}
	}

	if rlink[0] == 0 {
		// visit the solution
		if debug {
			fmt.Println("X2. Visit the solution")
		}
		if stats != nil {
			stats.Solutions++
		}
		lvisit()
		goto X8
	}

	// X3. [Choose i.]
	i = mrv()

	if debug {
		fmt.Printf("X3. Choose i=%d (%s)\n", i, name[i])
	}

	// X4. [Cover i.]
	if debug {
		fmt.Printf("X4. Cover i=%d (%s)\n", i, name[i])
	}
	cover(i)
	state[level] = dlink[i]

X5:
	// X5. [Try x_l.]
	if debug {
		fmt.Printf("X5. Try l=%d, x[l]=%d\n", level, state[level])
	}
	if state[level] == i {
		goto X7
	}
	p = state[level] + 1
	for p != state[level] {
		j := top[p]
		if j <= 0 {
			p = ulink[p]
		} else {
			cover(j)
			p++
		}
	}
	level++
	goto X2

X6:
	// X6. [Try again.]
	if debug {
		fmt.Println("X6. Try again")
	}

	if stats != nil {
		stats.Nodes++
	}

	p = state[level] - 1
	for p != state[level] {
		j = top[p]
		if j <= 0 {
			p = dlink[p]
		} else {
			uncover(j)
			p--
		}
	}
	i = top[state[level]]
	state[level] = dlink[state[level]]
	goto X5

X7:
	// X7. [Backtrack.]
	if debug {
		fmt.Println("X7. Backtrack")
	}
	uncover(i)

X8:
	// X8. [Leave level l.]
	if debug {
		fmt.Printf("X8. Leaving level %d\n", level)
	}
	if level == 0 {
		return
	}
	level--
	goto X6

}
