# language: pt

Funcionalidade: Envio de arquivo grande pelo cofre
  Como usuário da plataforma
  Quero enviar um documento grande dentro de um cofre
  Para visualizar na viewblob mesmo com um arquivo acima do tamanho comum

  @envio @ui @signature @critical
  Cenário: Envio de arquivo grande pelo cofre
    Dado que estou logado na plataforma D4Sign
    Quando envio um arquivo grande pelo cofre
    Então o documento deve estar aguardando signatários
