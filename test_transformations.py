#!/usr/bin/env python3
"""
Test script for transformation functions
"""

def test_transformations():
    # Test functions
    def mirror_words(x):
        if not x:
            return x
        words = x.split(' ')
        return ' '.join(word[::-1] for word in words)
    
    def encode_mirror_alphabet(x):
        if not x:
            return x
        result = ""
        for char in x:
            if char.isalpha():
                if char.islower():
                    result += chr(ord('z') - (ord(char) - ord('a')))
                else:
                    result += chr(ord('Z') - (ord(char) - ord('A')))
            else:
                result += char
        return result
    
    def toggle_case(x):
        if not x:
            return x
        return x.swapcase()
    
    def swap_pairs(x):
        if not x:
            return x
        words = x.split(' ')
        result_words = []
        for word in words:
            if len(word) <= 1:
                result_words.append(word)
            else:
                chars = list(word)
                for i in range(0, len(chars) - 1, 2):
                    chars[i], chars[i + 1] = chars[i + 1], chars[i]
                result_words.append(''.join(chars))
        return ' '.join(result_words)
    
    def encode_index_parity(x):
        if not x:
            return x
        words = x.split(' ')
        result_words = []
        for word in words:
            if len(word) <= 1:
                result_words.append(word)
            else:
                even_chars = [word[i] for i in range(0, len(word), 2)]
                odd_chars = [word[i] for i in range(1, len(word), 2)]
                result_words.append(''.join(even_chars + odd_chars))
        return ' '.join(result_words)
    
    def double_consonants(x):
        if not x:
            return x
        vowels = set('aeiouAEIOU')
        result = ""
        for char in x:
            result += char
            if char.isalpha() and char not in vowels:
                result += char
        return result
    
    # Reverse functions
    def reverse_double_consonants(x):
        if not x:
            return x
        vowels = set('aeiouAEIOU')
        result = ""
        i = 0
        while i < len(x):
            result += x[i]
            # If current char is a consonant and next char is the same, skip the duplicate
            if (i + 1 < len(x) and 
                x[i] == x[i + 1] and 
                x[i].isalpha() and 
                x[i] not in vowels):
                i += 1  # Skip the doubled consonant
            i += 1
        return result
    
    def reverse_encode_index_parity(x):
        if not x:
            return x
        words = x.split(' ')
        result_words = []
        for word in words:
            if len(word) <= 1:
                result_words.append(word)
            else:
                # Calculate original even and odd positions
                original_len = len(word)
                even_count = (original_len + 1) // 2
                
                even_chars = word[:even_count]
                odd_chars = word[even_count:]
                
                # Reconstruct by interleaving
                result_chars = [''] * original_len
                for i, char in enumerate(even_chars):
                    result_chars[i * 2] = char
                for i, char in enumerate(odd_chars):
                    if i * 2 + 1 < original_len:
                        result_chars[i * 2 + 1] = char
                
                result_words.append(''.join(result_chars))
        return ' '.join(result_words)
    
    # Test cases
    test_word = "HELLO WORLD"
    
    print(f"Original: {test_word}")
    
    # Test each transformation
    transformed = test_word
    print(f"Start: {transformed}")
    
    # Apply transformations
    transformed = encode_mirror_alphabet(transformed)
    print(f"After encode_mirror_alphabet: {transformed}")
    
    transformed = double_consonants(transformed)
    print(f"After double_consonants: {transformed}")
    
    transformed = mirror_words(transformed)
    print(f"After mirror_words: {transformed}")
    
    transformed = swap_pairs(transformed)
    print(f"After swap_pairs: {transformed}")
    
    transformed = encode_index_parity(transformed)
    print(f"After encode_index_parity: {transformed}")
    
    print(f"\nFinal transformed: {transformed}")
    
    # Now reverse the transformations
    print("\nReversing transformations:")
    
    # Reverse in opposite order
    current_word = transformed
    print(f"Start reverse: {current_word}")
    
    current_word = reverse_encode_index_parity(current_word)
    print(f"After reverse_encode_index_parity: {current_word}")
    
    current_word = swap_pairs(current_word)  # Self-inverse
    print(f"After reverse_swap_pairs: {current_word}")
    
    current_word = mirror_words(current_word)  # Self-inverse
    print(f"After reverse_mirror_words: {current_word}")
    
    current_word = reverse_double_consonants(current_word)
    print(f"After reverse_double_consonants: {current_word}")
    
    current_word = encode_mirror_alphabet(current_word)  # Self-inverse
    print(f"After reverse_encode_mirror_alphabet: {current_word}")
    
    print(f"\nFinal result: {current_word}")
    print(f"Expected: {test_word}")
    print(f"Match: {current_word == test_word}")

if __name__ == "__main__":
    test_transformations()
