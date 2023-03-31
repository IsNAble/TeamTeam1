const typingText = document.querySelector(".typing-text p"),
inpField = document.querySelector(".wrapper .input-field"),
tryAgainBtn = document.querySelector(".content button"),
timeTag = document.querySelector(".time span b"),
mistakeTag = document.querySelector(".mistake span"),
wpmTag = document.querySelector(".wpm span"),
cpmTag = document.querySelector(".cpm span");

let timer,
maxTime = 60,
countOfWords = 10,
timeLeft = maxTime,
charIndex = mistakes = isTyping = 0;

document.onload = function() {
    document.querySelector(".wrapper .input-field").focus();
}

function sendPostRequest(url) {
    return fetch(url, {
        method: 'POST',
        mode: 'no-cors'
    }).then(response => {
        return response
    })
}

function loadParagraph() {

    //const ranIndex = Math.floor(Math.random() * paragraphs.length);
    //let wordsListJson = JSON.parse(json); 

    let result = sample(JSON.parse(paragraphs), countOfWords),
    outputText = "";

    for (let i = 0; i < countOfWords; i++) {
        outputText += result[i] + ' ';
    }

    typingText.innerHTML = "";

    outputText.trim().split("").forEach(char => {
        let span = `<span>${char}</span>`
        typingText.innerHTML += span;
    });

    typingText.querySelectorAll("span")[0].classList.add("active");
    // document.addEventListener("keydown", () => inpField.focus());
    typingText.addEventListener("click", () => inpField.focus());
}

function initTyping() {
    let characters = typingText.querySelectorAll("span");
    let typedChar = inpField.value.split("")[charIndex];
    if(charIndex < characters.length - 1 && timeLeft > 0) {
        if(!isTyping) {
            timer = setInterval(initTimer, 1000);
            isTyping = true;
        }
        if(typedChar == null) {
            if(charIndex > 0) {
                charIndex--;
                if(characters[charIndex].classList.contains("incorrect")) {
                    mistakes--;
                }
                characters[charIndex].classList.remove("correct", "incorrect");
            }
        } else {
            if(characters[charIndex].innerText == typedChar) {
                characters[charIndex].classList.add("correct");
            } else {
                mistakes++;
                characters[charIndex].classList.add("incorrect");
            }
            charIndex++;
        }
        characters.forEach(span => span.classList.remove("active"));
        characters[charIndex].classList.add("active");

        let wpm = Math.round(((charIndex - mistakes)  / 5) / (maxTime - timeLeft) * 60);
        wpm = wpm < 0 || !wpm || wpm === Infinity ? 0 : wpm;
        
        wpmTag.innerText = wpm;
        mistakeTag.innerText = mistakes;
        cpmTag.innerText = charIndex - mistakes;
    } else {
        clearInterval(timer);

        let username = document.getElementById('username').innerText

        if (username !== '') {
            let url = "http://localhost:5000/typing-test/" + 
            username + '/' + wpmTag.innerText

            sendPostRequest(url)
        }

        inpField.value = "";
    }   
}

function getRandomWord(jsonObject) {
    let randomIndex = Math.floor(Math.random() * jsonObject.wordsList.length);

    return jsonObject.wordsList[randomIndex]
}


function sample(wordsListJson, countOfWord) {
    // Output list
    let sampleList = []

    for (let i = 0; i < countOfWord; i++) {
        let randomWord = getRandomWord(wordsListJson);
        while (randomWord.includes("'"))
            randomWord = getRandomWord(wordsListJson);

        sampleList.push(randomWord)
    }

    return sampleList;
}

function initTimer() {
    if(timeLeft > 0) {
        timeLeft--;
        timeTag.innerText = timeLeft;
        let wpm = Math.round(((charIndex - mistakes)  / 5) / (maxTime - timeLeft) * 60);
        wpmTag.innerText = wpm;
    } else {
        clearInterval(timer);
    }
}

function resetGame() {
    loadParagraph();
    clearInterval(timer);

    timeLeft = maxTime;
    charIndex = mistakes = isTyping = 0;
    inpField.value = "";
    timeTag.innerText = timeLeft;
    wpmTag.innerText = 0;
    mistakeTag.innerText = 0;
    cpmTag.innerText = 0;

    document.querySelector(".wrapper .input-field").focus();

}

loadParagraph();
inpField.addEventListener("input", initTyping);
tryAgainBtn.addEventListener("click", resetGame);