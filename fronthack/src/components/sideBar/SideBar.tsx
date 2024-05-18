import { useState } from 'react';
import axios from 'axios';
import logo from '../../img/logo.png';
import logoRJD from '../../img/logo_rjd.png';
import cross from '../../img/black-cross.png';
import loadingGif from '../../img/loading-gif.gif';
import download from '../../img/download.svg';
import Button from '../button/Button';
import InputFile from '../inputFile/InputFile';
import { useNavigate, Link } from 'react-router-dom';
import './style.scss';

type SideBaeProps = {
    setData: React.Dispatch<React.SetStateAction<any>>
};

const SideBar = (props: SideBaeProps): JSX.Element => {

    const [files, setFiles] = useState<File[]>();
    const [loading, setLoading] = useState<boolean>(false);
    const navigate = useNavigate();

    const handleSubmit: React.FormEventHandler<HTMLFormElement> = async (event: React.FormEvent<HTMLFormElement>) => {
        event.preventDefault();
        setLoading(true);

        if (files) {
            const formData = new FormData();
            [...files].forEach(file => {
                formData.append('file_uploads', file);
            })
            console.log(files);

            axios({
                url: `http://127.0.0.1:8000/upload`,
                method: "POST",
                data: formData,
                headers: { "Content-Type": "multipart/form-data" }
            })
                .then((response) => {
                    navigate('/result');
                    setLoading(false);
                    console.log(response.data);
                    props.setData(response.data);
                })
                .catch((error) => {
                    navigate('/warning');
                    setLoading(false);
                    console.log(error);
                    props.setData(undefined);
                });
        }
        else {
            navigate('/warning');
            setLoading(false);
            props.setData(undefined);
        }
    };

    return (
        <div className="side-bar">
            <div className="logo">
                <Link className='logo-link' to='/'>
                    <img className='logo-team' src={logo} alt="Логотип команды" />
                </Link>
                <img className='cross' src={cross} alt="Крестик" />
                <Link className='logo-link' to='https://www.rzd.ru/'>
                    <img className='logo-rjd' src={logoRJD} alt="Логотип РЖД" />
                </Link>
            </div>
            
            <div className="input-bar">
                <form className='form-data' name='form' onSubmit={handleSubmit} >
                    <div className="tittle-form">
                        <h2>Ввод</h2>
                    </div>
                    <hr />
                    <div className="choice-file">
                        <h3>Загрузите данные</h3>
                        <InputFile
                            text="Загрузить"
                            setFiles={setFiles}
                        >
                            <img
                                className=""
                                src={download}
                                alt="Загрузить"
                            />
                        </InputFile>
                    </div>
                    <hr />
                    <div className="submit">
                        <Button
                            className="btn-submit"
                            text="Анализ"
                            onClick={() => localStorage.clear()}
                        />
                    </div>
                    { loading ? <img className="loading-gif" src={loadingGif} alt="загрузка" /> : null }
                </form>
            </div>
        </div>
    );
};

export default SideBar; 
