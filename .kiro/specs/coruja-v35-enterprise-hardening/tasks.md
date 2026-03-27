root@srvcmonitor001:/home/administrador/CorujaMonitor# # Remover o container fantasma pelo ID
docker rm -f 0168ea8fe06a_coruja-api 2>/dev/null; true

# Listar todos os containers (incluindo parados) para ver o que sobrou
docker ps -a | grep api
0168ea8fe06a_coruja-api
root@srvcmonitor001:/home/administrador/CorujaMonitor# ^C
root@srvcmonitor001:/home/administrador/CorujaMonitor# docker-compose up -d --no-recreate api
Creating coruja-api ... done
root@srvcmonitor001:/home/administrador/CorujaMonitor# # Parar tudo, limpar containers parados, subir do zero
docker-compose down --remove-orphans
docker system prune -f
docker-compose up -d
Stopping coruja-api      ... done
Stopping coruja-frontend ... done
Stopping coruja-worker   ... done
Stopping coruja-ai-agent ... done
Stopping coruja-redis    ... done
Stopping coruja-postgres ... done
Stopping coruja-ollama   ... done
Removing coruja-api      ... done
Removing coruja-frontend ... done
Removing coruja-worker   ... done
Removing coruja-ai-agent ... done
Removing coruja-redis    ... done
Removing coruja-postgres ... done
Removing coruja-ollama   ... done
Removing network corujamonitor_default
Deleted build cache objects:
i621yobtlg2bbc6g1imq1f49u
30zgqqc030salkyvhpckvv0al
1au3eq1lyao9le0r1mrs7sx9d
5gwvff19rktca0m25ijg1fflb
xs3qtdpvka4o1srbxyy9prjhs
a2w0qcne6w6mj89cy8dd8f4rc
qeqg44oqheutyqqsbe3lo2zgn
u8x2pcuebkgjrs22hvb8ha7jy
j7wxwrwwq0x6eob8scmri6odg
axaznwwoa0xizbi1uk5a7cmbv
eonjvs3ryi1ngplhpdn6xgb6k
y0is88f2wqac6c8ka9p5syhf4
o46k9apuungj3r12nm5gkv56l
k0dcyxehy9yt5srqxl0oxab7f
wamih9g6k00nlq5jgd55wmsge
nx1ywan8jiz1h6nf4q91upeyt
kp6gnhrtd50q5qj39vjosot8x
999rgofqiy16l80no7evwvyu3
fn6xrqpjp1lt22x02cwxzrhj7
king06j48jpvru66hit0bzjxj
rohqfsfol0y4cdfopnr9gs962
vvdrvig6xanvmef14l2qrz8ra
qz81fu2tbn7be5mxddhu2o9zi
nfl1kn7dpoo518myppo30o7j6
ww6ibt68ym9tvc5gpc9rh10qp
f6j6aifd3cs4pi7ogz5uq59r5
cpj6r7p0mnh60muhwhoe2ajrm
pg2d90w31xgv05cegjx8jmfyq
yxm5inzajomek30vras5fq97q
qgsky0a8cnzdmzvf3qrqtfiav
jb49ur89gk5hk4oyan40wf0q3
7phx9v97gq1vi3lvlk77mp889
t6mlf78c60k4h5ttd1drtnq4u
pilafjj4iiu12ig9mfsizxkl1
jc2r6d8w6eodcksscsplcjvpy
r1l5o6113sub7lzbzoxkn0yqn
ie42i928j4wcxkvvzxh7fc596
dtf7ac1qvrx9p9humx6pwiunt
d9s7klgry79u2fh0qg434jmml
uvzkj9zg7fd6aitjuq3ulbrp0
gqihfu2hw5tl98syia33tumh1

Total reclaimed space: 6.856GB
Creating network "corujamonitor_default" with the default driver
Creating coruja-ollama   ... done
Creating coruja-postgres ... done
Creating coruja-redis    ... done
Creating coruja-worker   ... done
Creating coruja-ai-agent ... done
Creating coruja-api      ... done
Creating coruja-frontend ... done
Creating coruja-nginx    ... done
root@srvcmonitor001:/home/administrador/CorujaMonitor#
