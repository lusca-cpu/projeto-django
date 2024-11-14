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


//!---------Graficos---------------------->

function downloadPDF(itemToExport) {
    const item0 = document.querySelector("#content0");
    const item1 = document.querySelector("#content1");
    const item2 = document.querySelector("#content2");
    const item3 = document.querySelector("#content3");

    const loadingIndicator = document.createElement('div');
    loadingIndicator.textContent = "Generating PDF...";
    document.body.appendChild(loadingIndicator);

    // Criar um elemento temporário para concatenar os conteúdos
    const tempDiv = document.createElement('div');
    
    tempDiv.style.width = '100%';
    tempDiv.style.height = 'auto';
    tempDiv.style.overflow = 'visible';

    // Adicionar os conteúdos de acordo com o parâmetro
    if (itemToExport === 0) {
        tempDiv.appendChild(item0.cloneNode(true)); // Adiciona item0
    } else if (itemToExport === 1) {
        tempDiv.appendChild(item0.cloneNode(true)); // Adiciona item0
        tempDiv.appendChild(item1.cloneNode(true)); // Adiciona item1
    } else if (itemToExport === 2) {
        tempDiv.appendChild(item0.cloneNode(true)); // Adiciona item0
        tempDiv.appendChild(item2.cloneNode(true)); // Adiciona item2
    } else if (itemToExport === 3) {
        tempDiv.appendChild(item0.cloneNode(true)); // Adiciona item0
        tempDiv.appendChild(item3.cloneNode(true)); // Adiciona item3
    }

    // Verifica se existem imagens e aguarda o carregamento
    const images = tempDiv.querySelectorAll('img');
    let loadedImages = 0;

    images.forEach((img) => {
        img.onload = () => {
            loadedImages++;
            if (loadedImages === images.length) {
                generatePDF();
            }
        };
    });

    // Se não houver imagens, gera o PDF imediatamente
    if (images.length === 0) {
        generatePDF();
    }

    // Função para debouncing do redimensionamento do gráfico
    let timeout;
    const handleResize = () => {
        clearTimeout(timeout);
        timeout = setTimeout(() => {
            // Adicione aqui o código para redesenhar o gráfico, se necessário
            // Por exemplo: Plotly.redraw('meuGrafico'); // Altere para o ID do seu gráfico
        }, 200);
    };

    window.addEventListener('resize', handleResize);

    function generatePDF() {
        var opt = {
            margin: [0, 0, 0, 0], // [top, left, bottom, right]
            filename: "myfile.pdf",
            html2canvas: {
                scale: 2, 
                useCORS: true,
                image: { type: 'png', quality: 0.98 }
            },
            jsPDF: { unit: "mm", format: "letter", orientation: "portrait" },
        };
        
        html2pdf()
            .set(opt)
            .from(tempDiv)
            .save()
            .then(() => {
                loadingIndicator.remove(); // Remove loading indicator after saving
            })
            .catch((error) => {
                console.error("PDF generation failed:", error);
                loadingIndicator.textContent = "Failed to generate PDF.";
            })
            .finally(() => {
                window.removeEventListener('resize', handleResize); // Remove o listener após gerar o PDF
            });
    }
}

        // Obtém a data atual
        const dataAtual = new Date();
        
        // Formata a data no formato DD/MM/AAAA
        const dia = String(dataAtual.getDate()).padStart(2, '0');
        const mes = String(dataAtual.getMonth() + 1).padStart(2, '0'); // Mês é 0-indexado
        const ano = dataAtual.getFullYear();

        // Define a data formatada no elemento com id "data"
        document.getElementById('data').textContent = `${dia}/${mes}/${ano}`;