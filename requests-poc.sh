#!/bin/bash

for ((i=1; i<=10000; i++))
do
  start_time=$(date +%s%3N)
  
  echo -e "\nIteração $i"
  curl --location 'http://127.0.0.1:3211/chat/?query=contexto%3A%20voce%20esta%20lendo%20macro%20de%20um%20motorista%20monitorado%2C%20qual%20evento%20(EM%20DIRECAO%2C%20EM%20DESCANSO%2C%20EM%20REFEICAO%2C%20EM%20REPOUSO%2C%20EM%20ESPERA%2C%20PARADO%20EM%20JORNADA%2C%20EMBARQUE%20DE%20MOTORISTA%2C%20INICIO%20DE%20DIRECAO%2C%20FIM%20DE%20DIRECAO%2C%20DESEMBARQUE%20DE%20MOTORISTA%2C%20SEM%20POSICAO%20)%20est%C3%A1%20associado%20a%20descri%C3%A7%C3%A3o%20a%20seguir%3A%20esqueci%20de%20bater%20volta%20do%20almo%C3%A7o'
  
  end_time=$(date +%s%3N)
  elapsed_time=$((end_time - start_time))
  
  minutes=$((elapsed_time / 60000))
  seconds=$(((elapsed_time / 1000) % 60))
  milliseconds=$((elapsed_time % 1000))
  
  echo -e "\nResposta: $i tomou $minutes minutos, $seconds segundos e $milliseconds milissegundos\n\n"
done
