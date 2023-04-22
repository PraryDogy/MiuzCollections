data = [(1, 'sravan'), (1, 'ojaswi'), (1, 'bobby'),
        (4, 'rohith'), (4, 'gnanesh'),
        
        ]

images = {}

for num, word in data:
    images.setdefault(
        num, []
        ).append(word)
    
print(images)