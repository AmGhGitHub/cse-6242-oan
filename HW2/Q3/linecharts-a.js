const vlSpec_a = {
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",

  // your spec goes here
};

vegaEmbed('#svg-a', vlSpec_a, { renderer: 'svg' })
  .catch(console.error);

function vega_lite_spec_a() {
  return vlSpec_a;
}
function vega_spec_a() {
  return vegaLite.compile(vega_lite_spec_a()).spec;
}
