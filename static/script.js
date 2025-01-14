function fetchAvailableTimes(date) {
    fetch(`/available_slots?date=${date}`)
        .then(response => response.json())
        .then(data => updateTimes(data));
}

function updateTimes(data) {
    const availableContainer = document.getElementById('available-times');
    const reservedContainer = document.getElementById('reserved-times');
    availableContainer.innerHTML = '';
    reservedContainer.innerHTML = '';

    data.available_slots.forEach(time => {
        const card = createCard(time, false);
        availableContainer.appendChild(card);
    });

    data.reserved_slots.forEach(time => {
        const card = createCard(time, true);
        reservedContainer.appendChild(card);
    });
}

function createCard(time, reserved) {
    const card = document.createElement('div');
    card.className = 'card';
    if (reserved) {
        card.classList.add('reserved-card');
    }
    card.innerText = time;
    if (!reserved) {
        card.onclick = () => showPopup(time);
    }
    return card;
}

function showPopup(time) {
    document.getElementById('selected-time').innerText = `Hora Selecionada: ${time}`;
    document.getElementById('datetime').value = `${document.getElementById('date-picker').value} ${time}`;
    document.getElementById('popup').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
}

document.getElementById('overlay').onclick = function() {
    closePopup();
};

function closePopup() {
    document.getElementById('popup').style.display = 'none';
    document.getElementById('overlay').style.display = 'none';
}

document.getElementById('booking-form').onsubmit = function(event) {
    event.preventDefault();
    const formData = new FormData(this);
    fetch('/book', {
        method: 'POST',
        body: formData
    }).then(response => response.json())
      .then(data => {
          if (data.success) {
              closePopup();
              fetchAvailableTimes(document.getElementById('date-picker').value);
          } else {
              alert(data.message || 'Erro ao confirmar a reserva.');
          }
      });
};

document.getElementById('date-picker').value = new Date().toISOString().split('T')[0];
document.getElementById('date-picker').onchange = function() {
    fetchAvailableTimes(this.value);
};

fetchAvailableTimes(document.getElementById('date-picker').value);
