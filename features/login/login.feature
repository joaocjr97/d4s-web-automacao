# language: pt

Funcionalidade: Login na plataforma D4Sign
  Como usuário da plataforma
  Quero realizar login na D4Sign
  Para acessar o sistema de assinatura digital com segurança

  @login @smoke @critical
  Cenário: Login com sucesso
    Dado que acesso a página de login da D4Sign
    Quando realizo login com credenciais válidas
    Então devo ver o painel principal da plataforma

  @login
  Cenário: Login com senha incorreta
    Dado que acesso a página de login da D4Sign
    Quando realizo login com senha incorreta
    Então devo ver a mensagem de erro "E-mail ou senha inválida."
    E não devo estar autenticado na plataforma

  @login
  Cenário: Login com usuário inexistente
    Dado que acesso a página de login da D4Sign
    Quando realizo login com usuário inexistente
    Então devo ver a mensagem de erro "E-mail ou senha inválida."
    E não devo estar autenticado na plataforma

  @login
  Cenário: Login com e-mail em formato inválido
    Dado que acesso a página de login da D4Sign
    Quando realizo login com e-mail "email-invalido" e senha "SenhaTeste123"
    Então o campo e-mail deve exibir validação de formato inválido
    E não devo estar autenticado na plataforma

  @login
  Cenário: Login sem informar e-mail
    Dado que acesso a página de login da D4Sign
    Quando realizo login apenas com senha "SenhaTeste123"
    Então o campo e-mail deve exibir validação de preenchimento obrigatório
    E não devo estar autenticado na plataforma

  @login
  Cenário: Login sem informar senha
    Dado que acesso a página de login da D4Sign
    Quando realizo login apenas com e-mail válido
    Então o campo senha deve exibir validação de preenchimento obrigatório
    E não devo estar autenticado na plataforma

  @login
  Cenário: Login sem informar credenciais
    Dado que acesso a página de login da D4Sign
    Quando clico em entrar sem preencher os campos
    Então o campo e-mail deve exibir validação de preenchimento obrigatório
    E não devo estar autenticado na plataforma
