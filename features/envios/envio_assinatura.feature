# language: pt

Funcionalidade: Envio para assinatura pela desk
  Como usuário da plataforma
  Quero enviar documentos para assinatura
  Para coletar assinaturas digitais

  @envio @ui @signature @critical
  Cenário: Envio do documento pela desk
    Dado que estou logado na plataforma D4Sign
    Quando envio um documento pela desk para assinatura
    Então o documento deve estar aguardando signatários

  @envio @ui @signature @critical
  Cenário: Assinatura do documento pelo signatário
    Dado que o documento da desk está pronto para assinatura
    Quando adiciono signatário e envio o documento para assinatura
    E realizo a assinatura do documento
    Então a assinatura deve ser verificada com sucesso
