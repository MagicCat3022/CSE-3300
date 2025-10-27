set_of_letters = set()
with open('wordlist.txt', 'r') as f:
    words = f.read().splitlines()
    for word in words:
        set_of_letters.update(word)

print(''.join(sorted(set_of_letters)))