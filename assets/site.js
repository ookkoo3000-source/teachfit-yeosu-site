document.addEventListener('DOMContentLoaded', function(){
  var btn = document.querySelector('.menu-btn');
  var nav = document.querySelector('.mobile-nav-wrap');
  if(btn && nav){
    btn.addEventListener('click', function(){
      nav.classList.toggle('open');
    });
  }
});

/* 간편 상담 팝업: 처음 방문 시 한 번 자동으로 열림, 과목 → 학년·연락처 → formsubmit 전송 */
document.addEventListener('DOMContentLoaded', function(){
  var modal = document.getElementById('qModal');
  if(!modal) return;
  var box = modal.querySelector('.quick');
  var s1 = box.querySelector('.q-s1'), s2 = box.querySelector('.q-s2');
  function show(x){ s1.classList.remove('on'); s2.classList.remove('on'); x.classList.add('on'); }
  function open(){ modal.classList.add('open'); modal.setAttribute('aria-hidden','false'); }
  function close(){ modal.classList.remove('open'); modal.setAttribute('aria-hidden','true'); }
  var fab = document.getElementById('qFab');
  if(fab) fab.addEventListener('click', open);
  box.querySelector('.q-close').addEventListener('click', close);
  modal.addEventListener('click', function(e){ if(e.target === modal) close(); });
  document.addEventListener('keydown', function(e){ if(e.key === 'Escape') close(); });
  try {
    if(!sessionStorage.getItem('tf_quick')){ sessionStorage.setItem('tf_quick','1'); setTimeout(open, 1400); }
  } catch(_){ }
  box.querySelectorAll('.q-tiles button').forEach(function(b){
    b.addEventListener('click', function(){
      box.querySelector('.q-in-sub').value = b.getAttribute('data-s');
      box.querySelector('.q-chosen').textContent = b.getAttribute('data-s');
      box.querySelector('.q-hint').textContent = b.getAttribute('data-h');
      show(s2);
    });
  });
  box.querySelector('.q-back').addEventListener('click', function(){ show(s1); });
  var chips = box.querySelectorAll('.q-chips button');
  chips.forEach(function(b){
    b.addEventListener('click', function(){
      chips.forEach(function(x){ x.classList.remove('sel'); });
      b.classList.add('sel');
      box.querySelector('.q-in-grade').value = b.textContent;
    });
  });
  box.addEventListener('submit', function(){
    var btn = box.querySelector('.q-submit'); btn.disabled = true; btn.textContent = '접수 중…';
  });
});
