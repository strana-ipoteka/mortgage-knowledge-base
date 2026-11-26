(() => {
  // Tiles from https://github.com/melpnz/rblp, in image order, eight per row.
  const tiles = [
    ['sber', 'Сбербанк', 'Сбер'], ['vtb', 'Банк ВТБ', 'ВТБ'],
    ['dom', 'Банк Дом РФ', 'Дом РФ'], ['alfa', 'Альфа-Банк', 'Банк Альфа', 'Альфа'],
    ['metall', 'Металлинвестбанк', 'Металлинвест', 'Металл'], ['psb', 'Промсвязьбанк', 'Промсвязь', 'ПСБ'],
    ['absolut', 'Абсолют Банк', 'Абсолют'], ['uralsib', 'Банк Уралсиб', 'Уралсиб'],
    ['sovcom', 'Совкомбанк'], ['mkb', 'МКБ'],
    ['bspb', 'Банк Санкт-Петербург', 'Санкт-Петербург', 'Банк СПБ', 'БСПБ'],
    ['rshb', 'Россельхозбанк', 'Россельхоз', 'РСХБ'], ['vbrr', 'ВБРР'], ['rossiya', 'Банк Россия', 'Россия'],
    ['uralfd', 'Урал ФД'], ['gpb', 'Газпромбанк', 'Газпром', 'ГПБ'],
    ['atb', 'АТБ'], ['mts', 'МТС Банк', 'МТС'], ['tbank', 'Т-Банк', 'Тинькофф'],
    ['sngb', 'Сургутнефтегазбанк', 'СНГБ'], ['ubrr', 'УБРИР'], ['levob', 'Банк Левобережный', 'Левобережный'],
    ['novikom', 'Новикомбанк', 'Новокимбанк', 'Новиком'], ['akcept', 'Банк Акцепт', 'Акцепт'],
    ['tkb', 'Транскапиталбанк', 'Транскапитал', 'ТКБ'], ['primsoc', 'Примсоцбанк'],
    ['primorye', 'Банк Приморье', 'Приморье', 'Приморский'], ['akbars', 'Ак Барс Банк', 'Ак Барс'],
    ['dvb', 'Дальневосточный Банк', 'Дальневосточный', 'ДВБ'],
    ['rnkb', 'РНКБ'], ['raif', 'Райффайзенбанк', 'Райффайзен', 'Райф'],
    ['bfg', 'Банк Жилищного Финансирования', 'БЖФ', 'БФЖ'],
    ['severgaz', 'Севергазбанк', 'Севергаз'],
  ];
  const normalize = name => String(name ?? '').toLocaleLowerCase('ru')
    .replaceAll('ё', 'е').replace(/[^а-яa-z0-9]/g, '');
  const indexes = new Map(tiles.map(([id], index) => [id, index]));
  indexes.set('novokim', indexes.get('novikom'));
  const names = tiles.flatMap(([id, ...aliases]) => aliases.map(alias => [normalize(alias), id]))
    .sort(([a], [b]) => b.length - a.length);

  function identify(label) {
    const name = normalize(String(label ?? '').replace(/^КВ\s*·\s*/i, ''));
    return names.find(([alias]) => name.startsWith(alias))?.[1];
  }

  function icon(id) {
    const index = indexes.get(id);
    if (index === undefined) return '';
    const x = index % 8 / 7 * 100;
    const y = Math.floor(index / 8) / 4 * 100;
    return `<span class="bank-logo" aria-hidden="true" style="--bank-logo-x:${x}%;--bank-logo-y:${y}%"></span>`;
  }

  window.BankLogos = { identify, icon };
})();
