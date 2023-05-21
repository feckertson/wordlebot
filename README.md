# wordlebot
My attempts at a wordle bot. 

The basic idea is to define a \[quasi, semi\] metric on the list of all words and use it to partition a set of words based on a guess word 
then select a guess word which produces a high qulity partition in the sense that it has many, small equivalence classes.

I am using the five-letter words from the electronic scrabble dictionary ospd3 as the word list. It contains 8635 words.


There are various options for a metric which corresponds closely to the number and location of exact and inexact letter matches.
1. d(a, b) = 10 - #(a matches in b) - #(b matches in a)
   - yeilds at most 11 equivalence classes for each guess word.
2. d(a, b) = sum_i (alpha_i * 4^i) where alpha_i is zero if a\[i\] = b\[i\], else 1 if a\[i\] is matched in b and b\[i\] is matched in a, else 2 if a\[i\] is matched in b or b\[i\] is matched in a, else 3.
   - yields up to 4^5 = 2^10 equivalence clases for each guess word.
   - prioritzies earlier letters when computing distance, but the actual distances are not really relevant, just the equivalence classes.
3. r(a, b) = sum_i (alpha_i * 5^i) where alpha_i is zero if a\[i\] = b\[i\], else 1 if a\[i\] is matched in b and b\[i\] is matched in a, else 2 if a\[i\] is matched in b and b\[i\] is not matched in a, else 3 if a\[i\] is not matched in b and b\[i\] is matched in a, else 4.
   - this is a quasi metric.
   - it yeields up to 5^5 = 3125 potential equivalence classes.
   - matches the information about a guess word provided by wordle.


The cost to partition all words based on any one single guess is small (8635), but 
the cost to determine the partition for every guess is extemely high, 8635^2 = 74_563_225. Fortunately, 
that maneuver is only needed to determine the initial guess which can be determined once and hard-coded. 
Furthermore, the goal is to find an intial guess which produces an optimal partition and words that produce an inferior partition 
can identified rather quickly if maximum equivalence class size is used as a quality measure.

Each guess reduces the potential matches. 
When the number of potential matches is small, it is feasible to generate and examine every partition of the remaining words (8635*N steps).


