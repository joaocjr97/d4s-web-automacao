# language: pt

Funcionalidade: Template HTML
  Como usuário da plataforma
  Quero gerar documento via template HTML
  Para enviar e assinar digitalmente

  @envio @ui @template @regression @signature
  Cenário: Preenchimento do template no cofre
    Dado que estou logado na plataforma D4Sign
    Quando preencho e salvo um template HTML no cofre
    Então o template HTML deve estar pronto para envio

  @envio @ui @template @regression @signature 
  Cenário: Envio do documento gerado para assinatura
    Dado que estou logado na plataforma D4Sign
    E que o template HTML foi preenchido e salvo
    Quando envio o documento do template HTML para assinatura
    Então o documento deve estar na fase enviado

  @envio @ui @template @regression @signature
  Cenário: Assinatura do documento gerado
    Dado que estou logado na plataforma D4Sign
    E que o documento do template HTML foi enviado para assinatura
    Quando assino o documento do template HTML
    Então o template HTML deve estar assinado
