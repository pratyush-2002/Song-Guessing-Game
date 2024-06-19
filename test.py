year=
leap=False
if year%4==0 and not year%100 and year%400==0:
        leap=True
print(leap)