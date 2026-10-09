# language: pt

Funcionalidade: Validações de erro no envio
  Como usuário da plataforma
  Quero receber avisos claros ao cometer erros no envio
  Para corrigir o problema antes de prosseguir

  @envio @ui @signature @regression @erro
  Cenário: Envio para assinatura sem signatário
    Dado que estou logado na plataforma D4Sign
    E que enviei um documento pela desk
    Quando tento enviar para assinatura sem adicionar signatário
    Então devo ver o aviso para adicionar pelo menos um signatário

  @envio @ui @signature @regression @erro
  Cenário: Signatário com e-mail em formato inválido
    Dado que estou logado na plataforma D4Sign
    E que enviei um documento pela desk
    Quando adiciono signatário com e-mail "email-invalido"
    Então nenhum signatário deve ser adicionado à lista

  @envio @ui @signature @regression @erro 
  Cenário: Assinatura com senha incorreta
    Dado que estou logado na plataforma D4Sign
    E que enviei um documento pela desk
    Quando adiciono signatário e tento assinar com senha incorreta
    Então devo ver a mensagem de senha inválida
