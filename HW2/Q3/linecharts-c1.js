const vlSpec_c1 = {
  "$schema": "https://vega.github.io/schema/vega-lite/v6.json",
  // your spec goes here

};

vegaEmbed('#svg-c1', vlSpec_c1, { renderer: 'svg' }).catch(console.error);

function vega_lite_spec_c1() {
  return vlSpec_c1;
}
function vega_spec_c1() {
  return vegaLite.compile(vega_lite_spec_c1()).spec;
}
