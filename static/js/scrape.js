const redirectAnchor = d3.select("#redirect")
console.log(redirectAnchor)  // DEBUG

const sleep = (milliseconds) => {
    return new Promise(resolve => setTimeout(resolve, milliseconds))
}

if (redirectAnchor) {

    //wait 10 seconds, then redirect
    sleep(10000000).then(() => {
        window.location.replace(redirectAnchor.href)
    })

}