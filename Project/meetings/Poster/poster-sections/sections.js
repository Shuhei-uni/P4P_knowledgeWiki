document.querySelector('[data-review-toggle]')?.addEventListener('click',function(){
  const hidden=document.body.classList.toggle('no-review');
  this.setAttribute('aria-pressed',String(!hidden));
  this.textContent=hidden?'Show source notes':'Hide source notes';
});
document.querySelectorAll('img').forEach(img=>{
  const showFailure=()=>{
    if(img.dataset.failureShown)return;
    img.dataset.failureShown='true';
    const note=document.createElement('p');
    note.className='broken-asset';
    note.textContent='Figure did not load. This draft references an existing file: '+img.getAttribute('src')+'. Check that the draft remains inside the repository.';
    img.replaceWith(note);
  };
  img.addEventListener('error',showFailure);
  if(img.complete&&img.naturalWidth===0)showFailure();
});
