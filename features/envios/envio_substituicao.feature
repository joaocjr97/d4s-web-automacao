# language: pt

Funcionalidade: Substituição de documento
  Como usuário da plataforma
  Quero substituir o arquivo de um documento já enviado
  Para corrigir o conteúdo sem perder as configurações do envio

  @envio @ui @signature @regression
  Cenário: Substituição do arquivo de um documento enviado
    Dado que estou logado na plataforma D4Sign
    E que enviei um documento pela desk
    Quando substituo o arquivo do documento
    Então o documento deve exibir o novo arquivo aguardando signatários
