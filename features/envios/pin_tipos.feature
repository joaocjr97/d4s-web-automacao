# language: pt

Funcionalidade: Tipos de pin no documento
  Como usuário da plataforma
  Quero alternar o tipo do pin entre assinatura, rubrica e selo
  Para posicionar cada tipo de marcação no documento

  @envio @ui @signature @regression @pin
  Cenário: Alteração do tipo de pin entre assinatura, rubrica e selo
    Dado que estou logado na plataforma D4Sign
    Quando envio documento pelo cofre e adiciono pin no canvas
    E altero o tipo do pin para "Rubrica"
    Então o pin deve ser do tipo "Rubrica"
    Quando altero o tipo do pin para "Selo"
    Então o pin deve ser do tipo "Selo"
    Quando altero o tipo do pin para "Assinatura"
    Então o pin deve ser do tipo "Assinatura"
