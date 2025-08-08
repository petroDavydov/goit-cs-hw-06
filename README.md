##### goit-cs-hw-06
##### html, css, python, docker, MongodB, socket

### 1. Запуск проекту з папки goit-cs-hw-06

```
docker-compose -f docker/docker-compose.yaml up --build
```

### 2. Зупинка проекту

```
docker-compose -f docker/docker-compose.yaml down
```

### 3. Повне очищення з томами

```
docker-compose -f docker/docker-compose.yaml down -v
```

###### додаткові команди по бажанню

###### перезапуск після змін у коді
```
docker-compose -f docker/docker-compose.yaml up --build --force-recreate
```

######  Статус
```
docker ps
```

###### Запущені контейнери

```
docker volume ls
```

