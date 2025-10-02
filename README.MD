# 📘 Guia de Ambiente Python + Montagem de Unidade + Editor IDLE

Este guia mostra como:  

1. Criar e ativar um **ambiente virtual Python**.  
2. Listar dispositivos/partições disponíveis no sistema.  
3. Montar uma unidade de armazenamento com **UID** e **GID** do usuário.  
4. Abrir e usar o **editor gráfico IDLE** do Python.  

---

## 🐍 Criando um Ambiente Virtual em Python

1. Verifique a versão do Python:

```bash
python3 --version
```
Crie o ambiente virtual (exemplo: venv):

```bash

python3 -m venv venv
```
Ative o ambiente virtual:

Linux/macOS:

```bash

source venv/bin/activate
```
Para sair do ambiente virtual:

```bash

deactivate

```
💽 Listando as Partições Disponíveis
Liste todos os discos e partições conectados:

```bash
lsblk
```
Exemplo de saída:

```BASH

NAME        MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
mmcblk0     179:0    0 59.6G  0 disk 
├─mmcblk0p1 179:1    0  32G  0 part
├─mmcblk0p2 179:2    0  16G  0 part
No exemplo acima, a partição que queremos montar é /dev/mmcblk0p1.
```
📂 Montando a Unidade com Permissões de Usuário
Crie o ponto de montagem (se ainda não existir):

```bash

sudo mkdir -p /media/caninos/adata64
Obtenha o UID e GID do usuário atual:
```
```bash
id -u
id -g
```
Exemplo de saída:

```bash
1000
1000
```
Monte a unidade com seu usuário:

```bash

sudo mount -o uid=$(id -u),gid=$(id -g) /dev/mmcblk0p1 /media/caninos/adata64
```
Verifique se foi montado corretamente:

```bash

ls -l /media/caninos/adata64
```
Agora você deve ter acesso de leitura e escrita com o seu usuário.

✅ Desmontando a Unidade
Para remover com segurança:

```bash

sudo umount /media/caninos/adata64

```
🖥️ Usando o Editor IDLE no Python
O IDLE é o editor gráfico oficial que acompanha o Python.
Para abrir, use o comando:

```bash

python -m idlelib.idle
```
Isso abrirá a janela do IDLE, onde você pode escrever e executar seus códigos Python de forma interativa.






