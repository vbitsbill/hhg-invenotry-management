if (!window.printMyLabel) {
  window.printMyLabel = () => {
    const element = document.getElementsByName("barcode");
    console.log(element[0].innerText);

    if (!element.length) {
      throw new Error("Barcode not found");
    }

    var myHeaders = new Headers();
    myHeaders.append("Content-Type", "application/json");

    var raw = JSON.stringify([
      {
        type: "TEXT",
        data: element[0].innerText,
        size: 40,
        width: 0,
        alignment: 1,
        style: "BOLD_UNDERLINE",
      },
      {
        type: "QR",
        data: element[0].innerText,
        size: 8,
        width: 0,
        alignment: 1,
        style: "NONE",
      },
    ]);

    var requestOptions = {
      method: "POST",
      headers: myHeaders,
      body: raw,
    };

    fetch("http://localhost:8080/print", requestOptions)
      .then((response) => response.text())
      .then((result) => console.log(result))
      .catch((error) => console.log("error", error));
  };
}
