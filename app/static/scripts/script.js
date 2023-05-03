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