volatility = 0.645169
max_vol = 11592140.468
time = 0
volume = 68000


temp_impact = 0.142*(volatility)*(volume/(max_vol*(time/300)))**(0.6)
print(temp_impact)