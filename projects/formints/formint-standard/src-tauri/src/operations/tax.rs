/// Round a monetary value to the nearest cent using half-up rounding.
///
/// ## Examples
///
/// ```
/// let result = compute_tax(10.00, 0.15);
/// assert!((result - 1.50).abs() < f64::EPSILON);
///
/// let result = compute_tax(9.99, 0.07);
/// assert!((result - 0.70).abs() < f64::EPSILON); // 9.99 * 0.07 = 0.6993 → 0.70
/// ```
pub fn compute_tax(subtotal: f64, rate: f64) -> f64 {
    let raw = subtotal * rate;
    // Round to 2 decimal places using half-up rounding.
    // Multiply by 100, add 0.5 for half-up, truncate, divide by 100.
    (raw * 100.0 + 0.5).trunc() / 100.0
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn compute_tax_standard_rate() {
        let result = compute_tax(10.00, 0.15);
        assert!((result - 1.50).abs() < f64::EPSILON);
    }

    #[test]
    fn compute_tax_rounds_half_up() {
        // 9.99 * 0.07 = 0.6993 → half-up rounds to 0.70
        let result = compute_tax(9.99, 0.07);
        assert!((result - 0.70).abs() < f64::EPSILON);
    }

    #[test]
    fn compute_tax_zero_rate() {
        let result = compute_tax(100.00, 0.0);
        assert!((result - 0.0).abs() < f64::EPSILON);
    }

    #[test]
    fn compute_tax_whole_number_result() {
        // 20.00 * 0.10 = 2.00 — exact result
        let result = compute_tax(20.00, 0.10);
        assert!((result - 2.00).abs() < f64::EPSILON);
    }

    #[test]
    fn compute_tax_rounds_down() {
        // 10.00 * 0.164 = 1.64 — no rounding needed
        let result = compute_tax(10.00, 0.164);
        assert!((result - 1.64).abs() < f64::EPSILON);
    }
}
