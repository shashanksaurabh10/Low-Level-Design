# Interview Date - 5th Nov 2025
# Company - Microsoft

# Round - 1

# Question:
# Reverse words in a sentence, punctuations remain in their relative place - 
# Example-1
# # In: # Hello, World! 
# # Out: # World, Hello! 
# Example -2 
# # In: Well, she exclaimed "Oh No!". 
# # Out: No, Oh exclaimed "she Well!"


def reverse_words_keep_punctuations(sentence: str) -> str:
    # Step 1: Extract words manually
    words = []
    current = []
    
    for ch in sentence:
        if ch.isalnum():
            current.append(ch)
        else:
            if current:
                words.append(''.join(current))
                current = []
    if current:
        words.append(''.join(current))
    
    # Step 2: Reverse words
    reversed_words = words[::-1]
    
    # Step 3: Rebuild the sentence
    result = []
    word_index = 0
    i = 0
    while i < len(sentence):
        if sentence[i].isalnum():
            # Start of a word
            # Find word length
            j = i
            while j < len(sentence) and sentence[j].isalnum():
                j += 1
            # Replace this word with reversed one
            result.append(reversed_words[word_index])
            word_index += 1
            i = j
        else:
            result.append(sentence[i])
            i += 1
    
    return ''.join(result)


# 🧪 Examples
print(reverse_words_keep_punctuations("Hello, World!"))
# Output: World, Hello!

print(reverse_words_keep_punctuations('Well, she exclaimed "Oh No!".'))
# Output: No, Oh exclaimed "she Well!".

# -------------------------------------------
# Round - 2

# Question 1 - https://leetcode.com/problems/two-city-scheduling/description/

# A company is planning to interview 2n people. Given the array costs where costs[i] = [aCosti, bCosti], 
# the cost of flying the ith person to city a is aCosti, and the cost of flying the ith person to city b is bCosti.
# Return the minimum cost to fly every person to a city such that exactly n people arrive in each city.

def min_cost(cost):
    n = len(cost) // 2
    # Sort by difference in cost between city1 and city2
    cost.sort(key=lambda x: x[0] - x[1])
    
    total_cost = 0
    for i in range(len(cost)):
        if i < n:
            total_cost += cost[i][0]  # Send to city1
        else:
            total_cost += cost[i][1]  # Send to city2
            
    return total_cost

# Question - 2

# Given a matrix mat[][] and an integer x, the task is to check if x is present in mat[][] or not.
# Every row and column of the matrix is sorted in increasing order.

def matSearch(mat, x):
    n = len(mat)
    m = len(mat[0])
    i = 0
    j = m - 1

    while i < n and j >= 0:
        if x > mat[i][j]:
            i += 1
        elif x < mat[i][j]:
            j -= 1
        else:
            return True
    return False

if __name__ == "__main__":
    mat = [
        [3, 30, 38],
        [20, 52, 54],
        [35, 60, 69]
    ]
    x = 35
    if matSearch(mat, x):
        print("true")
    else:
        print("false")
