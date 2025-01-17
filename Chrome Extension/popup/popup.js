const button = document.getElementById('btn');
const tbody = document.getElementById('tbody');
const res = document.getElementById('res');

document.getElementById('text').innerText = new URLSearchParams(
  window.location.search
).get('text');

button.addEventListener('click', async () => {
  // const response = await fetch('đường dẫn tới backend nè anh');
  // const res = await response.json();
  const test = [
    {
      rank: 1,
      domain: 'danviet.vn',
      link: 'https://danviet.vn/ai-thong-tri-the-gioi-la-dieu-vo-ly-lo-bich-20230619024355931.htm',
      title:
        "'AI th\u1ed1ng tr\u1ecb th\u1ebf gi\u1edbi l\u00e0 \u0111i\u1ec1u v\u00f4 l\u00fd l\u1ed1 b\u1ecbch'",
      content: [
        'C\u00f3 m\u1ed9t n\u1ed7i s\u1ee3 h\u00e3i r\u1eb1ng khi tr\u00ed tu\u1ec7 nh\u00e2n t\u1ea1o t\u1ed5ng qu\u00e1t (AIG) t\u1ed3n t\u1ea1i, c\u00e1c nh\u00e0 khoa h\u1ecdc c\u00f3 th\u1ec3 k\u00edch ho\u1ea1t m\u1ed9t h\u1ec7 th\u1ed1ng si\u00eau th\u00f4ng minh s\u1ebd th\u1ed1ng tr\u1ecb th\u1ebf gi\u1edbi trong v\u00f2ng v\u00e0i ph\u00fat',
        'N\u0103m 2018, gi\u00e1o s\u01b0 LeCun gi\u00e0nh \u0111\u01b0\u1ee3c Gi\u1ea3i th\u01b0\u1edfng Turing c\u00f9ng v\u1edbi nh\u00e0 khoa h\u1ecdc Geoffrey Hinton v\u00e0 nh\u00e0 khoa h\u1ecdc m\u00e1y t\u00ednh Yoshua Bengio v\u00ec nh\u1eefng \u0111\u1ed9t ph\u00e1 v\u1ec1 tr\u00ed tu\u1ec7 nh\u00e2n t\u1ea1o',
        '"AI s\u1ebd th\u1ed1ng tr\u1ecb th\u1ebf gi\u1edbi? Kh\u00f4ng, n\u00f3 ch\u1ec9 l\u00e0 s\u1ef1 ph\u00f3ng chi\u1ebfu b\u1ea3n ch\u1ea5t con ng\u01b0\u1eddi l\u00ean m\u00e1y m\u00f3c", gi\u00e1o s\u01b0 LeCun n\u00f3i',
      ],
      similarity_percentage: 100,
      results: 'Những nguồn này dường như đều đồng ý rằng Trí tuệ nhân tạo sẽ không sớm thay thế con người trong việc trở thành quyền lực tối cao trên thế giới. Mặc dù có thể các hệ thống trí tuệ nhân tạo có thể đạt đến mức độ thông minh đáng kể và thậm chí vượt trội so với khả năng của con người, nhưng vẫn chưa rõ ràng khi nào điều này xảy ra hoặc liệu nó sẽ dẫn đến sự thay thế hoàn toàn cho tư duy con người hay không. Do đó, câu trả lời là Sai.'
    },
    {
      rank: 2,
      domain: 'vneconomy.vn',
      link: 'https://vneconomy.vn/techconnect//lieu-ai-va-robot-co-the-thong-tri-the-gioi.htm',
      title:
        'Li\u1ec7u AI v\u00e0 robot c\u00f3 th\u1ec3 th\u1ed1ng tr\u1ecb th\u1ebf gi\u1edbi?',
      content: [
        'Th\u1eadt th\u00fa v\u1ecb, nh\u1eefng robot tr\u00ean \u0111\u00e3 l\u00ean ti\u1ebfng c\u1ea3nh b\u00e1o con ng\u01b0\u1eddi n\u00ean ti\u1ebfn h\u00e0nh th\u1eadn tr\u1ecdng khi khai th\u00e1c ti\u1ec1m n\u0103ng ph\u00e1t tri\u1ec3n v\u01b0\u1ee3t b\u1eadc c\u1ee7a tr\u00ed tu\u1ec7 nh\u00e2n t\u1ea1o',
        'M\u1eb7c d\u00f9 nhi\u1ec1u ng\u01b0\u1eddi c\u1ea3m th\u1ea5y v\u1eabn c\u00f2n m\u1ed9t th\u1eddi gian d\u00e0i tr\u01b0\u1edbc khi AI v\u00e0 robot c\u00f3 th\u1ec3 l\u00e0m ch\u1ee7 cu\u1ed9c ch\u01a1i, theo m\u1ed9t s\u1ed1 c\u00e1ch, c\u00f4ng ngh\u1ec7 n\u00e0y \u0111\u00e3 chi\u1ebfm l\u0129nh th\u1ebf gi\u1edbi m\u00e0 nh\u00e2n lo\u1ea1i kh\u00f4ng nh\u1eadn ra',
        ' AI cung c\u1ea5p d\u1eef li\u1ec7u kh\u00f4ng thi\u00ean v\u1ecb trong khi con ng\u01b0\u1eddi th\u01b0\u1eddng s\u1eed d\u1ee5ng tr\u00ed tu\u1ec7 c\u1ea3m x\u00fac v\u00e0 s\u1ef1 s\u00e1ng t\u1ea1o \u0111\u1ec3 \u0111\u01b0a ra quy\u1ebft \u0111\u1ecbnh cu\u1ed1i c\u00f9ng", tuy\u00ean b\u1ed1 nh\u1ea5n m\u1ea1nh',
      ],
      similarity_percentage: 44,
      results: 'Những nguồn này dường như đều đồng ý rằng Trí tuệ nhân tạo sẽ không sớm thay thế con người trong việc trở thành quyền lực tối cao trên thế giới. Mặc dù có thể các hệ thống trí tuệ nhân tạo có thể đạt đến mức độ thông minh đáng kể và thậm chí vượt trội so với khả năng của con người, nhưng vẫn chưa rõ ràng khi nào điều này xảy ra hoặc liệu nó sẽ dẫn đến sự thay thế hoàn toàn cho tư duy con người hay không. Do đó, câu trả lời là Sai.'
    },
    {
      rank: 3,
      domain: 'tuoitre.vn',
      link: 'https://tuoitre.vn/cong-nghe-nam-2023-tri-tue-nhan-tao-hoc-may-se-thong-tri-20230101232551081.htm',
      title:
        'C\u00f4ng ngh\u1ec7 n\u0103m 2023: Tr\u00ed tu\u1ec7 nh\u00e2n t\u1ea1o, h\u1ecdc m\u00e1y s\u1ebd th\u1ed1ng tr\u1ecb',
      content: [
        'T\u1ea5t c\u1ea3 c\u00e1c d\u1ef1 b\u00e1o v\u1ec1 c\u00f4ng ngh\u1ec7 cho n\u0103m 2023 \u0111\u1ec1u nh\u1ea5t tr\u00ed r\u1eb1ng AI v\u00e0 machine learning s\u1ebd th\u1ed1ng tr\u1ecb n\u0103m m\u1edbi, th\u1ec3 hi\u1ec7n s\u1ef1 h\u1eefu \u00edch c\u1ee7a m\u00ecnh t\u1eeb v\u1ea5n \u0111\u1ec1 th\u1ee7 t\u1ee5c y t\u1ebf cho \u0111\u1ebfn d\u1ecbch v\u1ee5 ng\u00e2n h\u00e0ng',
        ' Metaverse h\u1ee9a h\u1eb9n t\u1ea1o ra m\u1ed9t th\u1ebf gi\u1edbi \u1ea3o c\u00f3 t\u00ednh t\u01b0\u01a1ng t\u00e1c cao v\u00e0 h\u1ea5p d\u1eabn',
        'Xu h\u01b0\u1edbng th\u1ee9 ba trong n\u0103m 2023 c\u1ee7a th\u1ebf gi\u1edbi s\u1ebd t\u1eadp trung theo h\u01b0\u1edbng ph\u00e1t tri\u1ec3n b\u1ec1n v\u1eefng',
      ],
      similarity_percentage: 44,
      results: 'Những nguồn này dường như đều đồng ý rằng Trí tuệ nhân tạo sẽ không sớm thay thế con người trong việc trở thành quyền lực tối cao trên thế giới. Mặc dù có thể các hệ thống trí tuệ nhân tạo có thể đạt đến mức độ thông minh đáng kể và thậm chí vượt trội so với khả năng của con người, nhưng vẫn chưa rõ ràng khi nào điều này xảy ra hoặc liệu nó sẽ dẫn đến sự thay thế hoàn toàn cho tư duy con người hay không. Do đó, câu trả lời là Sai.'
    },
  ];

  test.forEach((val, i, arr) => {
    const tr = `<tr>
    <td><a style="color: #5f4dee !important;" href=${val.link}>${val.title}</a></td>
    <td>${val.content.join(', ')}</td>
    </tr>`;
      tbody.insertAdjacentHTML('beforeend', tr);
    // In ra nội dung của thuộc tính `results` của phần tử cuối cùng
    if (i === arr.length - 1) {
      const lastResult = `<p><b>Kết luận:</b> ${val.results}</p>`;
      res.insertAdjacentHTML('beforeend', lastResult);
    }
  });

});

