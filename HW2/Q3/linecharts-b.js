const vlSpec_b = {
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  // your spec goes here
};

vegaEmbed('#svg-b', vlSpec_b, { renderer: 'svg' }).catch(console.error);

function vega_lite_spec_b() {
  return vlSpec_b;
}
function vega_spec_b() {
  return vegaLite.compile(vega_lite_spec_b()).spec;
}
