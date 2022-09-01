thumbs = [2019, 2020, 2021]*5
thumbs = [('image', i) for i in thumbs]



def split_years(thumbs):
    years = set(i[1] for i in thumbs)
    list_years = []

    for i in years:
]
        list_years.append([(img, year) for img, year in thumbs if year == i])

    return list_years

# 