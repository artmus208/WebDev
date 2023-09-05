const lower_date = document.getElementById('lower_date')
const upper_date = document.getElementById('upper_date')
function disable_date(checkboxElem) {
  if (checkboxElem.checked) {
    lower_date.disabled = true
    upper_date.disabled = true
  } else {
    lower_date.disabled = false
    upper_date.disabled = false
  }
}

// Вертикальный аккордеон
const stageHeaders = document.querySelectorAll('.accordion__header')
stageHeaders &&
  stageHeaders.forEach(item => {
    item.addEventListener('click', () => item.closest('.accordion').classList.toggle('accordion_open'))
  })

// Выделение текущего пункта
const reportsBtns = document.querySelectorAll('.reports-btns__btn ')
const windowLocationPathname = window.location.pathname

reportsBtns &&
  reportsBtns.forEach(btn => {
    console.log(windowLocationPathname)
    console.log(btn.href)
    btn.href.includes(windowLocationPathname.slice(0, -1)) && btn.querySelector('span').classList.add('underline')
  })
