function btn(chosenSong) {
    
    const xhr = new XMLHttpRequest();
    xhr.open('POST', 'http://127.0.0.1:5000/game', true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.onload = function() {
        if (this.status === 200) {
            const response = JSON.parse(this.responseText);
            document.getElementById("ha").innerHTML = 'SCORE: ' + response.score;
        } else {
            console.log("No score was sent");
        }
    };
    const params = JSON.stringify({ chosen_song: chosenSong });
    xhr.send(params);
}
document.querySelectorAll('.custom-button').forEach(button => {
    button.addEventListener('click', function() {
        document.querySelectorAll('.custom-button').forEach(btn => {
            btn.disabled = true;
        });
    });
});