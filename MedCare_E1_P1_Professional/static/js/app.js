(function(){
  const sidebar = document.querySelector('.sidebar');
  const hamburger = document.querySelector('.hamburger');

  if (!sidebar || !hamburger) return;

  const STORAGE_KEY = 'mc_sidebar_collapsed';

  function isMobile() {
    return window.innerWidth <= 900;
  }

  // restore collapsed state on desktop
  try {
    if (localStorage.getItem(STORAGE_KEY) === 'true') {
      sidebar.classList.add('collapsed');
    }
  } catch (e) {}

  hamburger.addEventListener('click', function(e){
    if (isMobile()) {
      // mobile: open/close overlay
      sidebar.classList.toggle('mobile-open');
      sidebar.classList.toggle('mobile-hidden', !sidebar.classList.contains('mobile-open'));
    } else {
      sidebar.classList.toggle('collapsed');
      try { localStorage.setItem(STORAGE_KEY, sidebar.classList.contains('collapsed') ? 'true' : 'false'); } catch (err) {}
    }

    // trigger layout/Chart.js redraw
    window.dispatchEvent(new Event('resize'));
  });

  // close sidebar when clicking outside on mobile
  document.addEventListener('click', function(e){
    if (!isMobile()) return;
    if (!sidebar.classList.contains('mobile-open')) return;
    if (!sidebar.contains(e.target) && !hamburger.contains(e.target)) {
      sidebar.classList.remove('mobile-open');
      sidebar.classList.add('mobile-hidden');
      window.dispatchEvent(new Event('resize'));
    }
  });

  // adapt on resize: ensure mobile classes reset
  window.addEventListener('resize', function(){
    if (!isMobile()) {
      sidebar.classList.remove('mobile-open', 'mobile-hidden');
    } else {
      if (!sidebar.classList.contains('mobile-open')) sidebar.classList.add('mobile-hidden');
    }
  });

  // ensure initial mobile-hidden for small screens
  if (isMobile() && !sidebar.classList.contains('mobile-open')) {
    sidebar.classList.add('mobile-hidden');
  }
})();
