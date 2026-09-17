// Third Party
import Form from 'react-bootstrap/Form';
import { useTranslation } from 'react-i18next';

type FormData = Record<string, string | boolean>;

interface AddSnapshotFormProps {
    formData: FormData;
    onChange: (data: FormData) => void;
    validated?: boolean;
}

/**
 * Renders the form for adding a snapshot to a survey session.
 * @param formData - The current form data.
 * @param onChange - Callback function to handle form data changes.
 * @param validated - Indicates whether the form has been validated.
 * @returns The JSX element for the add snapshot form.
 */
export default function AddSnapshotForm({
    formData,
    onChange,
    validated = false,
}: AddSnapshotFormProps) {
    const { t } = useTranslation();

    return (
        <Form noValidate className={validated ? 'was-validated' : ''}>
            <Form.Group controlId="raw_data" className="mb-3">
                <Form.Label>{t("Mining Result Data")}:</Form.Label>
                <Form.Control
                    as="textarea"
                    name="raw_data"
                    rows={12}
                    required
                    placeholder={t("Paste the 'Mining Survey' data here.")}
                    value={(formData.raw_data as string) ?? ''}
                    onChange={(e) => onChange({ ...formData, raw_data: e.target.value })}
                />
                <Form.Text className="text-muted d-block">
                    {t("Paste the 'Mining Survey' data here.")}
                </Form.Text>
                <Form.Control.Feedback type="invalid">
                    {t("Mining survey data is required.")}
                </Form.Control.Feedback>
            </Form.Group>
        </Form>
    );
}
