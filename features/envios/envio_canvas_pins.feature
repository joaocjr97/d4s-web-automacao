# language: pt

Funcionalidade: Canvas e pins
  Como usuário da plataforma
  Quero adicionar pin clicando no canvas
  Para validar posicionamento de assinatura

  @envio @ui @signature @critical
  Cenário: Adição de pin pelo canvas
    Dado que estou logado na plataforma D4Sign
    Quando envio documento pelo cofre e adiciono pin no canvas
    Então o pin deve estar visível no canvas
