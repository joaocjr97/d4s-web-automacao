# language: pt

Funcionalidade: Pin no documento
  Como usuário da plataforma
  Quero adicionar pins em documentos e anexos
  Para posicionar campos de assinatura

  @envio @ui @signature @critical @pin
  Cenário: Envio de documento com anexo e validação dos canvas
    Dado que estou logado na plataforma D4Sign
    Quando envio documento com anexo e valido os canvas
    Então o documento deve estar aguardando signatários

  @envio @ui @signature @critical @pin 
  Cenário: Replicação e remoção de pins em todas as páginas
    Dado que estou logado na plataforma D4Sign
    E que enviei documento com anexo no cofre
    Quando adiciono pin replicado e removo de todas as páginas
    Então os pins devem estar removidos de todas as páginas
