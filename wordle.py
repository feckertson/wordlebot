import re
from operator import itemgetter
from statistics import mean
from statistics import stdev

wordFile = open("c:/none-drive/documents/entertainment/word-games/ospd3_5.txt", "r")
wordList = list(map(lambda x: x.strip(), wordFile.readlines()))
wordFile.close()

# the words in a given list of words which fit the wordle repsonse to a given guess for a givein word.
def matchingWordsForGuess(words, word, guess):
  remainder = words
  for i in range(5):
    if word[i] == guess[i]:
      remainder = [w for w in remainder if w[i] == guess[i]]
    else:
      if guess[i] not in word:
        remainder = [w for w in remainder if guess[i] not in w]
      else:
        wcount = len([L for L in word if L == guess[i]])
        gcount = len([L for L in guess if L == guess[i]])
        if wcount < gcount:
          remainder = [w for w in remainder if len([L for L in w if L == guess[i]]) == wcount]
        remainder = [w for w in remainder if guess[i] in w and w[i] != guess[i]]
  return remainder


# the words in a given list of words which fit the wordle repsonses to a given list of guess for a givein word.
def matchingWordsForGuesses(words, word, guesses):
  remainder = words
  for guess in guesses:
    remainder = matchingWordsForGuess(remainder, word, guess)
  return remainder



# a "metric" which sums the letterwise distances between two five-letter words.
def score(iscore, g, w):
  return sum([(5**i)*iscore(g,w,i) for i in range(5)])

# a quasimetric from one word to another at the i-th letter position.
# matchin the wordle guess response (0=green; 1=yellow; 2=white)
def score3i(g,w,i):
  if g[i] == w[i]:
    return 0
  return 3

# a metric which measures the distance between two words at the i-th letter position. 
# this faults by counting duplicate "matches" even if both words do not duplcate the letter equally
# d('swore', 'spore', i) -> [0, 3, 0, 0, 0]
# d('esses', 'spell', i) -> [1, 2, 1, 2, 2]
def score4i(g,w,i):
  if g[i] == w[i]:
    return 0  
  a = g[i] in w
  b = w[i] in g
  if a and b:
    return 1
  if a or b: 
    return 2
  return 3


# a metric which measures the distance between two words at the i-th letter position. 
# this is slower but it takes care to only count duplicate "matches" only if both words duplicate the letter equally
# d('swore', 'spore', i) -> [0, 3, 0, 0, 0]
# d('esses', 'spell', i) -> [1, 2, 2, 3, 3]
def score5i(g,w,i):
  if g[i] == w[i]:
    return 0
  gI = len([j for j in range(i+1) if g[j] != w[j] and g[j] == g[i]])
  wI = len([j for j in range(i+1) if g[j] != w[j] and w[j] == w[i]])
  a = g[i] in w and (gI == 1 or gI <= len([j for j in range(5) if g[j] != w[j] and w[j] == g[i]]))
  b = w[i] in g and (wI == 1 or wI <= len([j for j in range(5) if g[j] != w[j] and g[j] == w[i]]))
  if a and b:
    return 1
  if a or b: 
    return 2
  return 3


# a non-reflexive measure of distance (quasimetric) from one word to another at the i-th letter position.
# has the advantage of supporting more outcomes.
# d('swore', 'spore', i) -> [0, 4, 0, 0, 0]
# d('esses', 'spell', i) -> [3, 1, 3, 1, 1]
# d('esses', 'spool', i) -> [2, 1, 1, 4, 1]
def score6i(g,w,i):
  if g[i] == w[i]:
    return 0  
  a = g[i] in w
  b = w[i] in g
  if a and b:
    return 3
  if b: 
    return 2
  if a: 
    return 1
  return 4



# a pseudometric which counts the letters which appear in only one of the two words
def d_match(s, w):
  return 10 - matchCount(s, w) - matchCount(w, s)
def matchCount(s,w):
  return len([i for i in range(5) if s[i] in w])



# partitions a set of words based on equal "distances" to a given guess word using a provided "metric" 
# but bails all words into a single class if any class size exceeds a specified maximum size.
def guessPartition(iscore, guess, words, m):
  wordsForScore = {}
  for w in words:
    s = score(iscore, guess, w)
    if not s in wordsForScore:
      wordsForScore[s] = []
    wordsForScore[s].append(w)
    if len(wordsForScore[s]) > m:
      wordsForScore = {}
      wordsForScore[len(words)] = words
      return wordsForScore
  return wordsForScore


def wordWordsWeightMSI(iscore, method, guess, words, m):
  partition = guessPartition(iscore, guess, words, m)
  if len(partition) == 1:
    return(len(words))
  match method:
    case 1:
      return mean([len(partition[k]) for k in partition])
    case 2:
      return max([len(partition[k]) for k in partition])/len(partition)
    case _:
      return max([len(partition[k]) for k in partition])


def bestGuessesInWordsSI(iscore, method, words, initialGuess=''):
  if (initialGuess):
    bestSoFar = wordWordsWeightMSI(iscore, method, initialGuess, words, len(words))
    bestWords = []
    bestWords.append(initialGuess)
  else:
    bestSoFar = len(words)
    bestWords = []
  for w in words:
    m = wordWordsWeightMSI(iscore, method, w, words, bestSoFar)
    if m == bestSoFar:
      bestWords.append(w)
    else:
      if m < bestSoFar:
        bestSoFar = m
        bestWords = []
        bestWords.append(w)
  return bestWords



def findWordSI(iscore, word, method = 0, initialGuess = "", outerCheck = False):
  guesses = []
  if initialGuess:
    guesses.append(initialGuess)
  else:
    if iscore in [score4i, score5i, score6i]:
      if method == 1:
        guesses.append('tares')
      else:
        guesses.append('stoae')
    else:
      guesses.append(bestGuessesInWordsSI(iscore, method, wordList, 'arose')[0][0])
  if guesses[-1] == word:
    print(guesses)
    return
  afterGuess = []
  afterGuess.append(matchingWordsForGuess(wordList, word, guesses[-1]))
  while len(afterGuess[-1]) > 1 and len(guesses) < 7:
    if outerCheck:
      guessLetters = ''
      for g in guesses:
        guessLetters += g
    if outerCheck and (2*len([i for i in range(5) if word[i] in [g[i] for g in guesses]]) + len([i for i in range(5) if word[i] not in [g[i] for g in guesses] and word[i] in guessLetters and len([j for j in range(i+1) if word[i] == word[j]]) <= max([len([j for j in range(5) if word[i] == g[j]]) for g in guesses])])) < 3:
      print("outer check")
      p = re.compile('.*[' + guessLetters + '].*')
      outer = [w for w in wordList if not p.match(w)]
      bgiw = bestGuessesInWordsSI(iscore, method, outer)
      nextGuess = bgiw[0]
      print("outer check found {}".format(nextGuess))
    else:
      bgiw = bestGuessesInWordsSI(iscore, method, afterGuess[-1])
      nextGuess = bgiw[0]
    guesses.append(nextGuess)
    print("next guess: {}".format(nextGuess))
    afterGuess.append(matchingWordsForGuess(afterGuess[-1], word, nextGuess))
  if afterGuess[-1] == [word] and nextGuess != word:
    guesses.append(word)      
  print(guesses)


findWordSI(score5i, 'shorn', 1)


findWordSI(score4i, 'cocoa', '', True)

# sed /[^thwspid]/d | grep a | grep r | grep e | sed /..a.../d | sed /.r..../d | sed /....e./d | wc -w

























letters = [chr(i) for i in range(97, 123)]
def getDeadLetters(word, guesses):
  usedLetters = set()
  for g in guesses:
    for l in g:
      if l not in word:
        usedLetters.add(l)
  return list(usedLetters)
  
matchCounts = []
for letter in letters:
  p = re.compile('.*' + letter + '.*')
  matches = [w for w in wordList if p.match(w)]
  matchCounts.append([letter, len(matches)])
matchCounts.sort(key=itemgetter(1), reverse=True)

matchCountPairs = []
for letter1 in letters:
  for letter2 in letters:
    p = re.compile('.*' + letter1 + letter2 + '.*')
    matches = [w for w in wordList if p.match(w)]
    matchCountPairs.append([letter1+letter2, len(matches)])
matchCountPairs.sort(key=itemgetter(1), reverse=True)




def identify0(theWord):
  filteredWords = wordList
  
  exactMatch = {}
  contains = {}
  absent = []
  maxOccur = {}
  
  guessWord = "arose"
  while len(exactMatch) < 5:
    print (guessWord)
    for l in guessWord:
      if len([i for i in range(5) if guessWord[i] == l]) > len([i for i in range(5) if theWord[i] == l]):
        maxOccur[l] = len([i for i in range(5) if theWord[i] == l])
    for i in range(5):
      if guessWord[i] == theWord[i]:
        exactMatch[i] = theWord[i]
      else:
        if guessWord[i] in theWord:
          if not guessWord[i] in contains:
            contains[guessWord[i]] = set();
          contains[guessWord[i]].add(i)
        else:
          absent.append(guessWord[i])
    filteredWords = [w for w in filteredWords if admitted0(w, exactMatch, contains, absent, maxOccur)]
#    print(filteredWords)
    weightedWords = [[w, sum([d_match(s, w) for s in filteredWords])] for w in filteredWords]
    weightedWords.sort(key = itemgetter(1))
    print(weightedWords)
    print(maxOccur)
    guessWord = weightedWords[0][0]


identify0("ghoul")


def admitted0(w, exactMatch, contains, absent, maxOccur):
  for i in exactMatch:
    if w[i] != exactMatch[i]:
      return False
  for l in absent:
    if l in w:
      return False
  for l in contains:
    for i in contains[l]:
      if w[i] == l:
        return False
  for l in maxOccur:
    if len([i for i in range(5) if w[i] == l]) > maxOccur[l]:
      return False
  return True





def score(g, w):
  ret = []
  for i in range(5):
    if g[i] == w[i]:
      ret.append (1)
    else:
      if g[i] not in w:
        ret.append (0)
      else:
        if len([j for j in range(5) if g[j] == w[j] and g[j] == g[i]]) + len([j for j in range(i+1) if g[j] != w[j] and g[j] == g[i]]) <= len([j for j in range(5) if w[j] == g[i]]):
          ret.append(-1)
        else:
          ret.append(-2)
  return ret

def scoreIt(s):
  ret = ''
  for i in range(5):
    match s[i]:
      case 0:
        ret += '0'
      case 1:
        ret += '1'
      case -1:
        ret += '*'
      case -2:
        ret += 'x'
  return ret

scoreValues = [0, 1, -1, -2]

scores = [scoreIt([a,b,c,d,e]) for a in scoreValues for b in scoreValues for c in scoreValues for d in scoreValues for e in scoreValues]

scoreTuples = [tuple([a,b,c,d,e]) for a in scoreValues for b in scoreValues for c in scoreValues for d in scoreValues for e in scoreValues]


scoreMap = {}
for t in scoreTuples:
  scoreMap[t] = scoreIt(t)
  

wordPairScores = [[g, w, scoreMap[tuple(score(g,w))]] for g in wordList for w in wordList]


scoredGuesses = {}
scoredGuesses[0] = {}
sg = scoredGuesses[0]
for t in wordPairScores:
  key = t[0] + '-' + t[2]
  if not key in sg:
    sg[key] = []
  sg[key].append(t[1])


guessScores = [[w, max([len(sg[k]) for k in sg if k > w and k < w+'A'])] for w in wordList]

sortedGuessScores = sorted(guessScores, key=itemgetter(1))


wordListSet = set(wordList)




for t in wordPairScores:
  if t[1] in afterGuessOneSet:
    key = t[0] + '-' + t[2]
    if not key in sg:
      sg[key] = set()
    sg[key].add(t[1])
  
guessScores = [[w, max([len(sg[k]) for k in sg if k > w and k < w+'A'])] for w in wordList]



letters = [chr(i) for i in range(97, 123)]
wordCountForLetter = {}
for L in letters:
  wordCountForLetter[L] = len([w for w in wordList if L in w])



weightedWords1 = [[w, sum([d_match(s, w) for s in filteredWords])] for w in wordList]
weightedWordsSorted1 = sorted(weightedWords, key=itemgetter(1))












def score10(g, w):
  ret = 0
  for i in range(5):
    if g[i] == w[i]:
      ret+=2
    else:
      if g[i] in w:
        if len([j for j in range(5) if g[j] == w[j] and g[j] == g[i]]) + len([j for j in range(i+1) if g[j] != w[j] and g[j] == g[i]]) <= len([j for j in range(5) if w[j] == g[i]]):
          ret+=1
  return 10-ret



distances = wordPairScores
scoredGuesses10 = []
scoredGuesses10.append({})
sg0 = scoredGuesses10[0]
for t in distances:
  if t[2] != 0:
    key = t[0] + '-' + str(t[2])
    if not key in sg0:
      sg0[key] = []
    sg0[key].append(t[1])


guessScores10 = [[w, [len(sg[k]) for k in sg if k > w and k < w+'A']] fow w in wordList]


[len(sg0[k]) for k in sg0 if k > 'stale' and k < 'staleA']




If only one or two guesses and known letters is less than three (count exact math double),



same
different but each in the other
dafferent and only one in the other
different and neither in the other








def wordWeights4(g):
  wordsForScore = {}
  for w in wordList:
    s = score4(g, w)
    if not s in wordsForScore:
      wordsForScore[s] = []
    wordsForScore[s].append(w)
  return [len(wordsForScore[k]) for k in wordsForScore]  

def wordWeightM4(g, m):
  wordsForScore = {}
  for w in wordList:
    s = score4(g, w)
    if not s in wordsForScore:
      wordsForScore[s] = []
    wordsForScore[s].append(w)
    if len(wordsForScore[s]) > m:
      return(len(wordList))
  return max([len(wordsForScore[k]) for k in wordsForScore])


bestSoFar = wordWeightM('stride', 1000)
bestWords = ['stride']
for w in wordList:
  m = wordWeightM(w, bestSoFar)
  if m == bestSoFar:
    bestWords.append(w)
  else:
    if m < bestSoFar:
      bestSoFar = m
      bestWords = []
      bestWords.append(w)





def score4(g, w): 
  return sum([(4**i)*score4i(g,w,i) for i in range(5)])

def wordWordsWeightM4(g, words, m):
  wordsForScore = {}
  for w in words:
    s = score4(g, w)
    if not s in wordsForScore:
      wordsForScore[s] = []
    wordsForScore[s].append(w)
    if len(wordsForScore[s]) > m:
      return(len(words))
  return max([len(wordsForScore[k]) for k in wordsForScore])


def bestGuessesInWords4(words, initialGuess=''):
  if (initialGuess):
    bestSoFar = wordWordsWeightM4(initialGuess, words, len(words))
    bestWords = []
    bestWords.append(initialGuess)
  else:
    bestSoFar = len(words)
    bestWords = []
  for w in words:
    m = wordWordsWeightM4(w, words, bestSoFar)
    if m == bestSoFar:
      bestWords.append(w)
    else:
      if m < bestSoFar:
        bestSoFar = m
        bestWords = []
        bestWords.append(w)
  return [bestSoFar, bestWords]




def score5(g, w): 
  return sum([(4**i)*score5i(g,w,i) for i in range(5)])


def wordWordsWeightM5(g, words, m):
  wordsForScore = {}
  for w in words:
    s = score5(g, w)
    if not s in wordsForScore:
      wordsForScore[s] = []
    wordsForScore[s].append(w)
    if len(wordsForScore[s]) > m:
      return(len(words))
  return max([len(wordsForScore[k]) for k in wordsForScore])


def bestGuessesInWords5(words, initialGuess=''):
  if (initialGuess):
    bestSoFar = wordWordsWeightM5(initialGuess, words, len(words))
    bestWords = []
    bestWords.append(initialGuess)
  else:
    bestSoFar = len(words)
    bestWords = []
  for w in words:
    m = wordWordsWeightM5(w, words, bestSoFar)
    if m == bestSoFar:
      bestWords.append(w)
    else:
      if m < bestSoFar:
        bestSoFar = m
        bestWords = []
        bestWords.append(w)
  return [bestSoFar, bestWords]








[i for i in range(5) if WORD[i] not in [g[i] for g in GUESSES] and WORD[i] in GUESSLETTERS and len([j for j in range(i+1) if WORD[i] == WORD[j]]) <= max([len([j for j in range(5) if WORD[i] == g[j]]) for g in GUESSES])]

[i for i in range(5) if word[i] not in [g[i] for g in guesses] and word[i] in guesslettersand len([j for j in range(i+1) if word[i] == word[j]]) <= max([len([j for j in range(5) if word[i] == g[j]]) for g in guesses])]

(2*len([i for i in range(5) if word[i] in [g[i] for g in guesses]]) + len([i for i in range(5) if word[i] not in [g[i] for g in guesses] and word[i] in guessLetters])) < 3:





wordPairScores = {}
for g in wordList:
  for w in wordList:
    wordPairScores[tuple([g, w])] = score(score5i, g, w)





























wordPairScoresV = [[g, w, score(score5i, g, w)] for g in wordList for w in wordList]


scoredGuesses = {}
scoredGuesses[0] = {}
sg = scoredGuesses[0]
for t in wordPairScoresV:
  key = t[0] + '-' + str(t[2])
  if not key in sg:
    sg[key] = []
  sg[key].append(t[1])


guessScores = [[w, max([len(sg[k]) for k in sg if k > w and k < w+'A'])] for w in wordList]
sortedGuessScores = sorted(guessScores, key=itemgetter(1))

guessScoresMean = [[w, mean([len(sg[k]) for k in sg if k > w and k < w+'A'])] for w in wordList]
sortedGuessScoresMean = sorted(guessScoresMean, key=itemgetter(1))



def bestGuesses(iscore, words):
  lenwords = len(words)
  if lenwords > 2 and lenwords < 20:
#    partitions = [[w, guessPartition(iscore, w, words, 1)] for w in wordList if not w in words]
    partitions = [[w, guessPartition(iscore, w, words, 1)] for w in wordList]
    partitions = [p for p in partitions if len(p[1]) > 1]
    if len(partitions) > 0:
      partitions = sorted([p for p in partitions ], key=lambda p: not p[0] in words) 
      print("splitting partition: {}".format(partitions[0]))
      return partitions
  partitions = [[w, guessPartition(iscore, w, words, lenwords)] for w in words]
  partitions = [p for p in partitions if len(p[1]) > 1]
  partitions = sorted(partitions, key=lambda p: max([len(p[1][s]) for s in p[1]]))
  print("len(partitions): {}".format(len(partitions)))
  return partitions


def bestGuesses(iscore, words):
  limit = len(words)
  partitions = [[w, guessPartition(iscore, w, words, limit)] for w in wordList]
  partitions = [p for p in partitions if len(p[1]) > 1]
  partitions = sorted(partitions, key=lambda p: max([len(p[1][s]) for s in p[1]]))
  minnax = len(partitions[0][1])
  print("minmax: {}".format(minnax))
  partitions = sorted([p for p in partitions if len(p[1]) == minnax], key=lambda p: not p[0] in words) 
  print("len(partitions): {}".format(len(partitions)))
  return partitions


def findWord(iscore, word, initialGuess = ""):
  guesses = []
  if initialGuess:
    guesses.append(initialGuess)
  else:
    guesses.append('tares')
  if guesses[-1] == word:
    return guesses
  afterGuess = []
  afterGuess.append(matchingWordsForGuess(wordList, word, guesses[-1]))
  while len(afterGuess[-1]) > 1 and len(guesses) < 7:
    nextGuess = bestGuesses(iscore, afterGuess[-1])[0][0]
    guesses.append(nextGuess)
    print("next guess: {}".format(nextGuess))
    afterGuess.append(matchingWordsForGuess(afterGuess[-1], word, nextGuess))
  if afterGuess[-1] == [word] and guesses[-1] != word:
    guesses.append(word)      
  return guesses
