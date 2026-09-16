// Third Party
import Form from 'react-bootstrap/Form';
import { useTranslation } from 'react-i18next';

type FormData = Record<string, string | boolean>;

interface CreateSessionFormProps {
    formData: FormData;
    onChange: (data: FormData) => void;
    validated?: boolean;
}

export default function CreateSessionForm({ formData, onChange, validated = false }: CreateSessionFormProps) {
    const { t } = useTranslation();

    return (
        <Form noValidate className={validated ? 'was-validated' : ''}>
            <Form.Group controlId="name" className="mb-3">
                <Form.Label>{t("Session Name")}:</Form.Label>
                <Form.Control
                    type="text"
                    name="name"
                    required
                    value={(formData.name as string) ?? ''}
                    onChange={(e) => onChange({ ...formData, name: e.target.value })}
                />
                <Form.Control.Feedback type="invalid">
                    {t("Session Name is required.")}
                </Form.Control.Feedback>
            </Form.Group>
            <Form.Group controlId="is_public">
                <Form.Check
                    type="checkbox"
                    name="is_public"
                    label={t("Public")}
                    checked={(formData.is_public as boolean) ?? false}
                    onChange={(e) => onChange({ ...formData, is_public: e.target.checked })}
                />
            </Form.Group>
        </Form>
    );
}
