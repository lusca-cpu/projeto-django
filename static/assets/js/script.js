window.addEventListener('DOMContentLoaded', event => {
    // Toggle the side navigation
    const sidebarToggle = document.body.querySelector('#sidebarToggle');
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', event => {
            event.preventDefault();
            document.body.classList.toggle('sb-sidenav-toggled');
            localStorage.setItem('sb|sidebar-toggle', document.body.classList.contains('sb-sidenav-toggled'));
        });
    }

    // Código para mostrar e ocultar o balão dos aplicativos
    var balloon = document.getElementById('popupBalloon');
    var button = document.getElementById('toggleButton');
    if (button && balloon) {
        button.addEventListener('mouseenter', function() {
            balloon.style.display = 'block';
        });
        button.addEventListener('mouseleave', function(event) {
            if (!balloon.contains(event.relatedTarget)) {
                balloon.style.display = 'none';
            }
        });
    }

    // Função para alternar a rotação de um ícone de seta (ou caret)
    var icon = document.getElementById('caretIcon');
    if (icon) {
        icon.addEventListener('click', function(event) {
            event.preventDefault();
            icon.classList.toggle('rotate-down');
        });
    }

    // Captura o evento de clique no botão editar e carrega o formulário via AJAX
    var editarButtons = document.querySelectorAll('.btn-editar-framework');
    editarButtons.forEach(function(button) {
        button.addEventListener('click', function() {
            var frameworkId = this.getAttribute('data-framework-id');
            fetch(`/framework/editar/${frameworkId}/`)
                .then(response => response.text())
                .then(html => {
                    document.querySelector('#editarFrameworkModal .modal-body').innerHTML = html;
                    var editarModal = new bootstrap.Modal(document.getElementById('editarFrameworkModal'));
                    editarModal.show();
                });
        });
    });

    // Função para mostrar e ocultar o campo de busca
    var searchInput = document.getElementById("searchInput");
    if (searchInput) {
        var searchButton = document.querySelector("button[onclick='toggleInput()']");
        if (searchButton) {
            searchButton.addEventListener('click', function() {
                toggleInput();
            });
        }
    }

    function toggleInput() {
        if (searchInput.style.display === "none") {
            searchInput.style.display = "inline-block";
            searchInput.focus();
        } else {
            searchInput.style.display = "none";
        }
    }
});

// Função para abrir uma nova janela em uma posição centralizada na tela do Draw.io
function abrirJanela(pagina, largura, altura) {
    var esquerda = (screen.width - largura) / 2;
    var topo = (screen.height - altura) / 2;
    minhaJanela = window.open(pagina, '', 'height=' + altura + ', width=' + largura + ', top=' + topo + ', left=' + esquerda);
}
