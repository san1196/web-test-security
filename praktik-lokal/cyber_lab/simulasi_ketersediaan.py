"""Simulasi antrian offline; tidak mengirim paket jaringan."""
CAPACITY=10;NORMAL=8;SUSPICIOUS=20;QUEUE_LIMIT=30
for limited in [False,True]:
    queue=0;dropped=0
    print('\nKontrol pembatasan:',limited)
    for tick in range(1,7):
        incoming=NORMAL+(2 if limited else SUSPICIOUS)
        queue+=incoming
        overflow=max(0,queue-QUEUE_LIMIT);dropped+=overflow;queue=min(queue,QUEUE_LIMIT)
        served=min(queue,CAPACITY);queue-=served
        print('t=',tick,'masuk=',incoming,'terlayani=',served,'antrian=',queue,'ditolak_kapasitas_total=',dropped)
print('\nModel edukasi; bukan benchmark dan bukan pembuktian DDoS.')
