function alternarMenu() {
    document.getElementById('menuLateral').classList.toggle('aberto');
}

function mostrarTela(id, btn) {
    const telas = document.querySelectorAll('.tela');
    const itensMenu = document.querySelectorAll('.item-menu');

    telas.forEach(tela => {
        tela.classList.remove('ativa');
        tela.style.display = "none"; 
    });
    
    itensMenu.forEach(item => item.classList.remove('ativo'));

    const telaAtiva = document.getElementById(id);
    if (telaAtiva) {
        telaAtiva.classList.add('ativa');
        telaAtiva.style.display = "block"; 
        if(btn) btn.classList.add('ativo');
    }
}

// Busca e Carrossel
document.addEventListener('DOMContentLoaded', () => {
    const inputBusca = document.getElementById('inputBuscaClinica');
    if (inputBusca) {
        inputBusca.addEventListener('input', function() {
            const termo = this.value.toLowerCase();
            document.querySelectorAll('.card-clinica').forEach(card => {
                const nome = card.querySelector('h3').textContent.toLowerCase();
                card.style.display = nome.includes(termo) ? "block" : "none";
            });
        });
    }
    carrosselAutomatico();
});

let indice = 0;
function carrosselAutomatico() {
    const slides = document.getElementsByClassName("slide-carrossel");
    const pontos = document.getElementsByClassName("ponto");
    if (slides.length === 0) return;
    for (let i = 0; i < slides.length; i++) slides[i].style.display = "none";
    indice++;
    if (indice > slides.length) indice = 1;
    for (let i = 0; i < pontos.length; i++) pontos[i].className = pontos[i].className.replace(" ativo", "");
    if(slides[indice-1]) slides[indice-1].style.display = "block";
    if(pontos[indice-1]) pontos[indice-1].className += " ativo";
    setTimeout(carrosselAutomatico, 5000);
}

document.addEventListener('DOMContentLoaded', () => {
    const inputBusca = document.getElementById('inputBuscaClinica');
    
    // Função de Busca em Tempo Real
    if (inputBusca) {
        inputBusca.addEventListener('input', function() {
            const termoBusca = this.value.toLowerCase();
            const cards = document.querySelectorAll('.card-clinica');

            cards.forEach(card => {
                const nomeClinica = card.querySelector('h3').textContent.toLowerCase();
                
                if (nomeClinica.includes(termoBusca)) {
                    card.style.display = "flex"; // Mostra o card
                } else {
                    card.style.display = "none"; // Esconde o card
                }
            });
        });
    }
});

// Função para trocar de tela (Caso precise)
function mostrarTela(id, btn) {
    document.querySelectorAll('.tela').forEach(t => t.classList.remove('ativa'));
    document.querySelectorAll('.item-menu').forEach(i => i.classList.remove('ativo'));
    
    const telaDestino = document.getElementById(id);
    if (telaDestino) {
        telaDestino.classList.add('ativa');
        btn.classList.add('ativo');
    }
}

function mostrarTela(id, btn) {
    // Esconde todas as telas
    document.querySelectorAll('.tela').forEach(t => t.classList.remove('ativa'));
    
    // Remove a classe ativo de todos os botões
    document.querySelectorAll('.item-menu').forEach(i => i.classList.remove('ativo'));
    
    // Mostra a tela selecionada e ativa o botão
    const tela = document.getElementById(id);
    if (tela) {
        tela.classList.add('ativa');
        btn.classList.add('ativo');
        
        // No mobile, faz o scroll subir ao trocar de tela
        window.scrollTo({ top: 0, behavior: 'smooth' });
        document.querySelector('.area-conteudo').scrollTo({ top: 0, behavior: 'smooth' });
    }
}

// Funções do Modal
function abrirModal(clinica, dentista, data, hora, procedimento, endereco) {
    const modal = document.getElementById('modalDetalhes');
    
    // Preenche os campos do modal
    document.getElementById('modalClinica').innerText = clinica;
    document.getElementById('modalEndereco').innerText = endereco;
    document.getElementById('modalDentista').innerText = dentista;
    document.getElementById('modalDataHora').innerText = `${data} às ${hora}`;
    document.getElementById('modalProcedimento').innerText = procedimento;
    
    
    
    modal.style.display = 'flex';
}

function fecharModal() {
    document.getElementById('modalDetalhes').style.display = 'none';
}

// Fecha o modal ao clicar fora dele
window.onclick = function(event) {
    const modal = document.getElementById('modalDetalhes');
    if (event.target == modal) {
        fecharModal();
    }
}

// Variável para controlar se estamos no modo visualização ou edição
let modoEdicao = false;

function fecharModal() {
    document.getElementById('modalDetalhes').style.display = 'none';
    resetarModal(); // Garante que o modal volte ao estado inicial ao fechar
}

function resetarModal() {
    modoEdicao = false;
    document.getElementById('infoConsulta').style.display = 'block';
    document.getElementById('formReagendar').style.display = 'none';
    document.getElementById('btnAcaoPrincipal').innerText = 'Reagendar';
    document.getElementById('btnAcaoPrincipal').style.background = 'var(--azul-claro)';
}

function prepararReagendamento() {
    const info = document.getElementById('infoConsulta');
    const form = document.getElementById('formReagendar');
    const btn = document.getElementById('btnAcaoPrincipal');

    if (!modoEdicao) {
        // Entra no modo de escolha de data
        info.style.display = 'none';
        form.style.display = 'block';
        btn.innerText = 'Confirmar Nova Data';
        btn.style.background = 'var(--verde-sucesso)';
        modoEdicao = true;
    } else {
        // Lógica para Salvar o Reagendamento
        const data = document.getElementById('novaData').value;
        const hora = document.getElementById('novoHorario').value;

        if (data && hora) {
            // Aqui você faria a chamada para o banco de dados futuramente
            alert(`Sucesso! Sua consulta foi reagendada para ${data} às ${hora}.`);
            
            // Atualiza visualmente o modal (opcional)
            document.getElementById('modalDataHora').innerText = `${data} às ${hora}`;
            
            fecharModal();
        } else {
            alert("Por favor, selecione a data e o horário.");
        }
    }
}

function trocarAba(event, abaId) {
    // Esconde todos os conteúdos
    document.querySelectorAll('.conteudo-aba').forEach(aba => {
        aba.classList.remove('ativa');
    });

    // Remove classe ativa de todos os botões
    document.querySelectorAll('.aba-item').forEach(btn => {
        btn.classList.remove('ativa');
    });

    // Mostra a aba clicada e ativa o botão
    document.getElementById(abaId).classList.add('ativa');
    event.currentTarget.classList.add('ativa');
}

function verDetalhesClinica(nome, email, tel, desc) {
    // 1. Esconde as outras telas
    document.querySelectorAll('.tela').forEach(t => t.style.display = 'none');
    
    // 2. Preenche os dados (Opcional se quiser tornar dinâmico)
    if(nome) document.getElementById('detalheNomeClinica').innerText = nome;
    
    // 3. Mostra a tela de perfil centralizada
    const telaPerfil = document.getElementById('perfil-clinica');
    telaPerfil.style.display = 'flex';
    
    // 4. Sobe a página para o topo
    window.scrollTo(0, 0);
}

function voltarParaInicio() {
    document.getElementById('perfil-clinica').style.display = 'none';
    document.getElementById('inicio').style.display = 'block'; // ajuste para sua ID de home
}

function trocarAba(event, abaId) {
    // Esconde todas com efeito de saída
    const conteudos = document.querySelectorAll('.aba-conteudo');
    conteudos.forEach(aba => {
        aba.style.display = 'none';
        aba.classList.remove('ativa');
    });

    // Desativa botões
    const botoes = document.querySelectorAll('.aba-item');
    botoes.forEach(btn => btn.classList.remove('ativa'));

    // Ativa aba selecionada
    const abaAtiva = document.getElementById('aba-' + abaId);
    abaAtiva.style.display = 'flex';
    setTimeout(() => abaAtiva.classList.add('ativa'), 10);

    // Ativa botão selecionado
    event.currentTarget.classList.add('ativa');
}

document.addEventListener('DOMContentLoaded', function() {
    // Seleção dos elementos
    const btnAbrir = document.getElementById('btn-abrir-agendamento');
    const modal1 = document.getElementById('modal-agendamento-1');
    const modal2 = document.getElementById('modal-agendamento-2');
    const modalSucesso = document.getElementById('modal-sucesso');

    // 1. Abrir o primeiro Pop-up
    if (btnAbrir) {
        btnAbrir.onclick = function() {
            modal1.style.display = 'flex';
        };
    }

    // 2. Ir para a segunda etapa
    window.proximaEtapa = function() {
        modal1.style.display = 'none';
        modal2.style.display = 'flex';
    };

    // 3. Confirmar e mostrar sucesso
    window.confirmarAgendamento = function() {
        modal2.style.display = 'none';
        modalSucesso.style.display = 'flex';
    };

    // 4. Fechar ao clicar fora do modal (Opcional)
    window.onclick = function(event) {
        if (event.target.className === 'modal') {
            event.target.style.display = 'none';
        }
    };
});

function irParaMeusAgendamentos() {
    // 1. Esconder o modal de sucesso
    const modalSucesso = document.getElementById('modal-sucesso');
    if (modalSucesso) modalSucesso.style.display = 'none';

    // 2. Esconder todas as seções que têm a classe 'tela'
    const todasAsTelas = document.querySelectorAll('.tela');
    todasAsTelas.forEach(tela => {
        tela.style.display = 'none';
    });

    // 3. Mostrar especificamente a seção de consultas
    const telaConsultas = document.getElementById('consultas');
    if (telaConsultas) {
        telaConsultas.style.display = 'block'; // Ou 'flex', dependendo do seu CSS
    };
};

document.getElementById("btnLogout").addEventListener("click", function(e) {
    e.preventDefault();
    
    // Opcional: Limpar dados de sessão se estiver usando localStorage
    // localStorage.removeItem('usuario_logado');

    // Redireciona de volta para a tela de login
    window.location.href = "../../Login_e_Cadastro/html/login.html";
});