(function(){
  function init(){
    var nav = document.querySelector('.topnav');
    if(!nav) return;
    var btn = nav.querySelector('.nav-toggle');
    var links = nav.querySelector('.nav-links');
    if(!btn || !links) return;
    btn.addEventListener('click', function(){
      var open = nav.classList.toggle('open');
      btn.setAttribute('aria-expanded', open ? 'true' : 'false');
    });
    // Close menu on link click (mobile)
    links.addEventListener('click', function(e){
      if(e.target.tagName === 'A' && nav.classList.contains('open')){
        nav.classList.remove('open');
        btn.setAttribute('aria-expanded','false');
      }
    });
  }
  if(document.readyState === 'loading')
    document.addEventListener('DOMContentLoaded', init);
  else init();
})();

