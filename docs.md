## Glossary
#### Properties
- `axial` Axial properties have 2 values, one for each axis.
    - `horizontal` The first axial property
    - `vertical` The second axial property
    - `along` The axis aligned with the layout axis
    - `across` The axis perpendicular to the layout axis
- `cardinal` Directional properties have 4 values, two for each axis.
    - `top` The first vertical property
    - `right` The second horizontal property
    - `bottom` The second vertical property
    - `left` The first horizontal property

#### Units
- `string` Any string
- `literal` A keyword string
- `pixel (px)` One character in the console. A pixel is twice as tall as it is wide
- `square (sq)` Two characters in the console. This unit is the same size in any axis
- `percentage (%)` A value relative to the parent
- `dimensionless` A value without unit

#### Sizing
- `static` Static node sizing does not depend on anything
- `dynamic` Dynamic node sizing depends on the parent, children and siblings
    - `grow` Growing nodes size themselves to fill available space inside parent
    - `fit` Fitted nodes size themselves to fit their content, shrinking further if required to fit inside parent
- `relative` Relative node sizing only depends on the parent

#### Positioning
- `automatic` Node position depends on siblings and parent
- `manual` Node position does not depend on, or influence the positioning of other elements
    - `relative` Relative nodes share their origin with their parent
    - `absolute` Absolute nodes share their origin with the layout
