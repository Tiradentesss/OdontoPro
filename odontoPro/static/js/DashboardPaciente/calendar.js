/**
 * Calendar & Time Selector
 * Calendário interativo com seletor de horários
 */

class CalendarTimeSelector {
  constructor(options = {}) {
    this.currentDate = new Date();
    this.selectedDate = null;
    this.selectedTime = null;
    this.container = options.container || '.calendar-container';
    this.minDate = options.minDate || new Date();
    this.maxDate = options.maxDate || new Date(new Date().setMonth(new Date().getMonth() + 3));
    this.availableTimes = options.availableTimes || this.getDefaultTimes();
    this.onDateChange = options.onDateChange || (() => {});
    this.onTimeChange = options.onTimeChange || (() => {});
    
    this.init();
  }

  init() {
    this.renderCalendar();
    this.attachEventListeners();
  }

  renderCalendar() {
    const year = this.currentDate.getFullYear();
    const month = this.currentDate.getMonth();
    
    // Get first day of month and number of days
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();
    
    let html = '';
    
    // Day headers
    const dayNames = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
    dayNames.forEach(day => {
      html += `<div class="day-header">${day}</div>`;
    });
    
    // Previous month days
    for (let i = firstDay - 1; i >= 0; i--) {
      const day = daysInPrevMonth - i;
      html += `<div class="day-cell other-month disabled">${day}</div>`;
    }
    
    // Current month days
    const today = new Date();
    for (let day = 1; day <= daysInMonth; day++) {
      const currentCellDate = new Date(year, month, day);
      const dateString = this.formatDate(currentCellDate);
      const isToday = this.isToday(currentCellDate);
      const isSelected = this.selectedDate && dateString === this.formatDate(this.selectedDate);
      const isWeekend = currentCellDate.getDay() === 0 || currentCellDate.getDay() === 6;
      
      let classes = 'day-cell';
      if (isToday) classes += ' today';
      if (isSelected) classes += ' selected';
      if (isWeekend) classes += ' weekend';
      
      html += `<div class="${classes}" data-date="${dateString}">${day}</div>`;
    }
    
    // Next month days
    const totalCells = firstDay + daysInMonth;
    const remainingCells = 42 - totalCells; // 6 rows × 7 days
    for (let day = 1; day <= remainingCells; day++) {
      html += `<div class="day-cell other-month disabled">${day}</div>`;
    }
    
    // Procurar e atualizar a matriz visível
    const matrices = document.querySelectorAll('.calendar-matrix');
    matrices.forEach(matrix => {
      // Verificar se a matriz está visível (dentro de um modal que está aberto)
      const modal = matrix.closest('.modal');
      if (modal && modal.classList.contains('mostrar')) {
        matrix.innerHTML = html;
      }
    });
    
    // Update month/year display - procurar o mês/ano correspondente
    const monthNames = ['January', 'February', 'March', 'April', 'May', 'June',
                       'July', 'August', 'September', 'October', 'November', 'December'];
    const monthYearEls = document.querySelectorAll('.month-year');
    monthYearEls.forEach(el => {
      const modal = el.closest('.modal');
      if (modal && modal.classList.contains('mostrar')) {
        el.textContent = `${monthNames[month]} ${year}`;
      }
    });
  }

  attachEventListeners() {
    // Delegação: dia clicado no calendário
    const calendarMatrix = document.querySelector('.calendar-matrix');
    if (calendarMatrix) {
      calendarMatrix.addEventListener('click', (event) => {
        const dayCell = event.target.closest('.day-cell');
        if (!dayCell || dayCell.classList.contains('other-month') || dayCell.classList.contains('disabled')) {
          return;
        }
        this.selectDate(dayCell);
      });
    }

    // Delegação para campos de horário
    const timeSlotsContainer = document.querySelector('.time-slots');
    if (timeSlotsContainer) {
      timeSlotsContainer.addEventListener('click', (event) => {
        const slot = event.target.closest('.time-slot');
        if (!slot || slot.classList.contains('unavailable')) {
          return;
        }
        this.selectTime(slot);
        setTimeout(() => {
          const modal = document.getElementById('modal-horarios');
          if (modal) {
            modal.classList.remove('mostrar');
            modal.style.display = 'none';
          }
        }, 200);
      });
    }
    
    // Navigation buttons
    const prevBtn = document.getElementById('btn-prev-month');
    const nextBtn = document.getElementById('btn-next-month');
    const todayBtn = document.querySelector('.btn-today');
    
    if (prevBtn) {
      const newPrevBtn = prevBtn.cloneNode(true);
      prevBtn.parentNode.replaceChild(newPrevBtn, prevBtn);
      newPrevBtn.addEventListener('click', () => this.previousMonth());
    }
    
    if (nextBtn) {
      const newNextBtn = nextBtn.cloneNode(true);
      nextBtn.parentNode.replaceChild(newNextBtn, nextBtn);
      newNextBtn.addEventListener('click', () => this.nextMonth());
    }
    
    if (todayBtn) {
      const newTodayBtn = todayBtn.cloneNode(true);
      todayBtn.parentNode.replaceChild(newTodayBtn, todayBtn);
      newTodayBtn.addEventListener('click', () => this.goToToday());
    }
  }

  selectDate(element) {
    const dateString = element.dataset.date;
    if (!dateString) return;
    
    this.selectedDate = new Date(dateString);
    
    // Update UI
    document.querySelectorAll('.day-cell.selected').forEach(el => {
      el.classList.remove('selected');
    });
    element.classList.add('selected');
    
    // Update aside section
    const dayNum = this.selectedDate.getDate();
    const monthName = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
                      [this.selectedDate.getMonth()];
    
    const asideNum = document.querySelector('.aside-date');
    const asideMonth = document.querySelector('.aside-month');
    if (asideNum) asideNum.textContent = dayNum;
    if (asideMonth) asideMonth.textContent = monthName;
    
    this.onDateChange(this.selectedDate);

    // Atualizar input direto (garantir que o valor ficou setado)
    const inputData = document.getElementById('inputData');
    if (inputData) {
      inputData.value = dateString;
    }

    // Fechar modal de calendário após selecionar data
    setTimeout(() => {
      const modal = document.getElementById('modal-calendario');
      if (modal) {
        modal.classList.remove('mostrar');
        modal.style.display = 'none';
      }
    }, 300);
  }

  selectTime(element) {
    if (element.classList.contains('unavailable')) return;
    
    this.selectedTime = element.textContent.trim();
    
    // Update UI
    document.querySelectorAll('.time-slot.selected').forEach(el => {
      el.classList.remove('selected');
    });
    element.classList.add('selected');
    
    this.onTimeChange(this.selectedTime);
  }

  previousMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() - 1);
    this.renderCalendar();
    this.attachEventListeners();
  }

  nextMonth() {
    this.currentDate.setMonth(this.currentDate.getMonth() + 1);
    this.renderCalendar();
    this.attachEventListeners();
  }

  goToToday() {
    this.currentDate = new Date();
    this.renderCalendar();
    this.attachEventListeners();
  }

  isToday(date) {
    const today = new Date();
    return date.getDate() === today.getDate() &&
           date.getMonth() === today.getMonth() &&
           date.getFullYear() === today.getFullYear();
  }

  formatDate(date) {
    const year = date.getFullYear();
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
  }

  getDefaultTimes() {
    const times = [];
    for (let hour = 8; hour <= 17; hour++) {
      for (let minute of ['00', '30']) {
        times.push(`${String(hour).padStart(2, '0')}:${minute}`);
      }
    }
    return times;
  }

  renderTimeSlots() {
    let html = '';
    this.availableTimes.forEach(time => {
      html += `<div class="time-slot" data-time="${time}">${time}</div>`;
    });
    
    // Tentar renderizar em .time-slots (pode haver múltiplos)
    const containers = document.querySelectorAll('.time-slots');
    containers.forEach(container => {
      container.innerHTML = html;
    });
    
    this.attachEventListeners();
  }

  getSelectedDateTime() {
    if (!this.selectedDate || !this.selectedTime) return null;
    
    return {
      date: this.formatDate(this.selectedDate),
      time: this.selectedTime,
      dateTime: `${this.formatDate(this.selectedDate)} ${this.selectedTime}`
    };
  }

  reset() {
    this.selectedDate = null;
    this.selectedTime = null;
    this.currentDate = new Date();
    this.renderCalendar();
    this.renderTimeSlots();
    this.attachEventListeners();
  }
}

// Initialize calendar when page loads
function initializeCalendarSelector() {
  // Procurar por calendar-matrix tanto em .calendar-container quanto em #modal-calendario
  const calendarMatrices = document.querySelectorAll('.calendar-matrix');
  
  if (calendarMatrices.length === 0) {
    console.warn('Calendar matrix não encontrado');
    return;
  }
  
  // Usar o último calendar-matrix visível (o do modal)
  const visibleMatrix = Array.from(calendarMatrices).find(m => {
    return m.closest('.modal') && m.closest('.modal').classList.contains('mostrar');
  }) || calendarMatrices[calendarMatrices.length - 1];
  
  if (!visibleMatrix) {
    console.warn('Nenhum calendar-matrix visível encontrado');
    return;
  }
  
  console.log('Inicializando calendário...');
  
  // Limpar calendar anterior se existir
  if (window.calendarSelector) {
    window.calendarSelector = null;
  }
  
  window.calendarSelector = new CalendarTimeSelector({
    onDateChange: (date) => {
      console.log('Selected date:', date);
      
      // Update form field if exists
      const dateInput = document.getElementById('inputData');
      if (dateInput) {
        const year = date.getFullYear();
        const month = String(date.getMonth() + 1).padStart(2, '0');
        const day = String(date.getDate()).padStart(2, '0');
        dateInput.value = `${year}-${month}-${day}`;
        console.log('Data input atualizado:', dateInput.value);
      }
      
      // Atualizar display da data selecionada
      const dataSelecionadaDisplay = document.getElementById('dataSelecionadaDisplay');
      if (dataSelecionadaDisplay) {
        const monthNames = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho',
                           'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'];
        const dayName = date.toLocaleDateString('pt-BR', { weekday: 'short' });
        const dateStr = `${dayName}, ${day} de ${monthNames[parseInt(month) - 1]} de ${year}`;
        dataSelecionadaDisplay.innerHTML = `<span>${dateStr}</span><i class="fa-solid fa-calendar" style="margin-left: 10px; color: #00BCD4;"></i>`;
      }
    },
    onTimeChange: (time) => {
      console.log('Selected time:', time);
      
      // Update form field if exists
      const timeInput = document.getElementById('selectHorario');
      if (timeInput) {
        // Create option if not exists
        let option = timeInput.querySelector(`option[value="${time}"]`);
        if (!option) {
          option = document.createElement('option');
          option.value = time;
          option.textContent = time;
          timeInput.appendChild(option);
        }
        timeInput.value = time;
        console.log('Horário input atualizado:', time);
      }
      
      // Atualizar display da hora selecionada
      const horaSelecionadaDisplay = document.getElementById('horaSelecionadaDisplay');
      if (horaSelecionadaDisplay) {
        horaSelecionadaDisplay.innerHTML = `<span>${time}</span><i class="fa-solid fa-clock" style="margin-left: 10px; color: #00BCD4;"></i>`;
      }
    }
  });

  // Render time slots
  window.calendarSelector.renderTimeSlots();
  console.log('Calendário inicializado com sucesso');
}

document.addEventListener('DOMContentLoaded', () => {
  // Aguardar um pouco para garantir que o DOM está completo
  setTimeout(() => {
    initializeCalendarSelector();
  }, 1000);
});
