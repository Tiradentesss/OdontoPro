(function(){
    'use strict';

    function onlyDigits(v){ return (v||'').toString().replace(/\D/g,''); }

    function maskCPF(v){
        v = onlyDigits(v).slice(0,11);
        if(!v) return '';
        if(v.length <=3) return v;
        if(v.length <=6) return v.replace(/(\d{3})(\d+)/, '$1.$2');
        if(v.length <=9) return v.replace(/(\d{3})(\d{3})(\d+)/, '$1.$2.$3');
        return v.replace(/(\d{3})(\d{3})(\d{3})(\d{1,2})/, '$1.$2.$3-$4');
    }

    function maskCNPJ(v){
        v = onlyDigits(v).slice(0,14);
        if(!v) return '';
        if(v.length <=2) return v;
        if(v.length <=5) return v.replace(/(\d{2})(\d+)/, '$1.$2');
        if(v.length <=8) return v.replace(/(\d{2})(\d{3})(\d+)/, '$1.$2.$3');
        if(v.length <=12) return v.replace(/(\d{2})(\d{3})(\d{3})(\d+)/, '$1.$2.$3/$4');
        return v.replace(/(\d{2})(\d{3})(\d{3})(\d{4})(\d{1,2})/, '$1.$2.$3/$4-$5');
    }

    function maskPhone(v){
        v = onlyDigits(v).slice(0,11);
        if(!v) return '';
        if(v.length <=2) return '('+v;
        if(v.length <=6) return v.replace(/(\d{2})(\d+)/, '($1) $2');
        if(v.length <=10) return v.replace(/(\d{2})(\d{4})(\d+)/, '($1) $2-$3');
        return v.replace(/(\d{2})(\d{5})(\d{1,4})/, '($1) $2-$3');
    }

    function formatValue(input){
        const mask = input.dataset.mask;
        const raw = onlyDigits(input.dataset.raw ?? input.value);
        let formatted = raw;
        if(mask === 'cpf') formatted = maskCPF(raw);
        else if(mask === 'cnpj') formatted = maskCNPJ(raw);
        else if(mask === 'phone') formatted = maskPhone(raw);
        else return input.value;
        input.dataset.raw = raw;
        input.dataset.formatted = formatted;
        return formatted;
    }

    function onInput(e){
        const input = e.target;
        const selectionStart = input.selectionStart;
        input.dataset.raw = onlyDigits(input.value);
        input.value = formatValue(input);
        // move cursor to end (simple approach)
        try{ input.setSelectionRange(input.value.length, input.value.length); } catch(err){}
    }

    function initInput(input){
        if(!input) return;
        const mask = input.dataset.mask;
        if(!mask) return;
        // initialize from server value
        input.dataset.raw = onlyDigits(input.value || input.dataset.value || '');
        input.value = formatValue(input);
        input.addEventListener('input', onInput);
        // ensure paste is normalized
        input.addEventListener('paste', (ev) => {
            ev.preventDefault();
            const paste = (ev.clipboardData || window.clipboardData).getData('text') || '';
            input.dataset.raw = onlyDigits(paste);
            input.value = formatValue(input);
        });
    }

    document.addEventListener('DOMContentLoaded', () => {
        const masked = document.querySelectorAll('input[data-mask]');
        masked.forEach(initInput);

        // on form submit, replace masked values with raw digits
        document.querySelectorAll('form').forEach(form => {
            form.addEventListener('submit', () => {
                masked.forEach(input => {
                    if(!form.contains(input)) return;
                    const raw = input.dataset.raw ?? onlyDigits(input.value);
                    input.value = raw;
                });
                // restore formatted values shortly after submit so UI remains consistent
                setTimeout(() => masked.forEach(initInput), 200);
            });
        });
    });

})();
