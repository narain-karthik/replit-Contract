document.addEventListener('DOMContentLoaded', () => {
  // Set today's date in any #date fields
  document.querySelectorAll('#date').forEach(input => {
    try {
      const today = new Date();
      input.value = today.toISOString().split('T')[0];
    } catch (e) {}
  });

  // Initialize autocomplete where present
  const docInput = document.getElementById('document_number');
  const revInput = document.getElementById('revision_number');
  const docSug = document.getElementById('doc_suggestions');
  const revSug = document.getElementById('rev_suggestions');

  if (docInput && revInput && docSug && revSug) {
    setupAutocomplete(docInput, revInput, docSug, revSug);
  }

  // Close suggestions when clicking outside any autocomplete wrap
  document.addEventListener('click', (e) => {
    const inWrap = e.target.closest('.autocomplete-wrap');
    if (!inWrap) {
      document.querySelectorAll('.suggestions').forEach(div => div.innerHTML = '');
    }
  });

  // Master Documents Line Items logic (without changing backend functions)
  const addFieldBtn = document.getElementById('addFieldBtn');
  const saveAllBtn = document.getElementById('saveAllBtn');
  const itemsWrap = document.getElementById('lineItems');

  if (addFieldBtn && itemsWrap) {
    addFieldBtn.addEventListener('click', () => {
      const first = itemsWrap.querySelector('.line-row');
      if (!first) return;
      const clone = first.cloneNode(true);
      clone.querySelectorAll('input').forEach(i => (i.value = ''));
      // Add remove button if not present
      ensureRemoveButton(clone);
      itemsWrap.appendChild(clone);
    });

    // Ensure initial row has a non-active remove; next rows can remove
    itemsWrap.querySelectorAll('.line-row').forEach((row, idx) => {
      if (idx === 0) {
        ensureRemoveButton(row, /*disabled*/ true);
      } else {
        ensureRemoveButton(row);
      }
    });
  }

  if (saveAllBtn && itemsWrap) {
    saveAllBtn.addEventListener('click', async () => {
      const sharedDoc = document.getElementById('shared_document_number')?.value || document.getElementById('document_number')?.value || '';
      const sharedRev = document.getElementById('shared_revision_number')?.value || document.getElementById('revision_number')?.value || '';
      const sharedStatus = document.getElementById('shared_status')?.value || document.getElementById('status')?.value || 'ACTIVE';

      const rows = Array.from(itemsWrap.querySelectorAll('.line-row'));
      const validRows = rows.map(row => {
        const get = (name) => row.querySelector(`input[name="${name}"]`)?.value?.trim() || '';
        const quantity = get('quantity');
        const material_number = get('material_number');
        const material_name = get('material_name');
        const vendor = get('vendor');
        const price = get('price');
        // Skip completely empty rows
        const hasAny = [quantity, material_number, material_name, vendor, price].some(Boolean);
        return hasAny ? { quantity, material_number, material_name, vendor, price } : null;
      }).filter(Boolean);

      if (validRows.length === 0) {
        alert('Nothing to save. Please add or fill at least one row.');
        return;
      }

      // Disable button during save
      const originalText = saveAllBtn.textContent;
      saveAllBtn.disabled = true;
      saveAllBtn.textContent = 'Saving...';

      try {
        // Post each row individually to the same endpoint (no backend change)
        for (const row of validRows) {
          const fd = new FormData();
          fd.set('quantity', row.quantity);
          fd.set('material_number', row.material_number);
          fd.set('material_name', row.material_name);
          fd.set('vendor', row.vendor);
          fd.set('document_number', sharedDoc);
          fd.set('revision_number', sharedRev);
          fd.set('price', row.price);
          fd.set('status', sharedStatus);

          await fetch('/master/documents', { method: 'POST', body: fd, credentials: 'same-origin' });
        }
        window.location.href = '/master/documents';
      } catch (err) {
        console.error(err);
        alert('Failed to save all rows. Please try again.');
      } finally {
        saveAllBtn.disabled = false;
        saveAllBtn.textContent = originalText;
      }
    });
  }
});

/* Helpers */
function ensureRemoveButton(row, disabled = false) {
  let holder = row.querySelector('.row-actions');
  if (!holder) {
    holder = document.createElement('div');
    holder.className = 'row-actions';
    row.appendChild(holder);
  } else {
    holder.innerHTML = '';
  }
  const btn = document.createElement('button');
  btn.type = 'button';
  btn.className = 'remove-row';
  btn.title = disabled ? 'Cannot remove the first row' : 'Remove this row';
  btn.innerHTML = disabled ? '—' : '×';
  if (!disabled) {
    btn.addEventListener('click', () => {
      row.remove();
    });
  } else {
    btn.disabled = true;
    btn.style.opacity = 0.5;
    btn.style.cursor = 'not-allowed';
  }
  holder.appendChild(btn);
}

function setupAutocomplete(docInput, revInput, docSug, revSug) {
  const fetchData = async (term) => {
    const res = await fetch(`/api/search_documents?term=${encodeURIComponent(term)}`, { credentials: 'same-origin' });
    return res.ok ? res.json() : [];
  };

  // Render helpers
  const clear = (el) => el && (el.innerHTML = '');
  const renderItems = (el, items, onClick) => {
    clear(el);
    items.forEach(t => {
      const div = document.createElement('div');
      div.className = 'suggestion-item';
      div.textContent = t;
      div.addEventListener('click', () => onClick(t));
      el.appendChild(div);
    });
  };

  // Document number autocomplete
  docInput.addEventListener('input', async function () {
    const term = this.value.trim();
    if (!term) return clear(docSug);
    const data = await fetchData(term);
    const uniqueDocs = Array.from(new Set(data.map(d => d.document_number).filter(Boolean)));
    renderItems(docSug, uniqueDocs, (picked) => {
      docInput.value = picked;
      // If there is exactly one revision for this doc in results, auto-fill rev
      const revs = Array.from(new Set(data.filter(d => d.document_number === picked).map(d => d.revision_number).filter(Boolean)));
      if (revs.length === 1) revInput.value = revs[0];
      clear(docSug);
    });
  });

  // Revision number autocomplete
  revInput.addEventListener('input', async function () {
    const term = this.value.trim();
    if (!term) return clear(revSug);
    const data = await fetchData(term);
    const uniqueRevs = Array.from(new Set(data.map(d => d.revision_number).filter(Boolean)));
    renderItems(revSug, uniqueRevs, (picked) => {
      revInput.value = picked;
      clear(revSug);
    });
  });
}